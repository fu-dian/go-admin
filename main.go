package main

import (
	"net/http"
	"strconv"
	"github.com/gin-contrib/cors"
	"time"
	"github.com/gin-gonic/gin"
	"github.com/go-playground/validator/v10"
	"gorm.io/driver/mysql"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"

	"go-user-admin/model"
)

var (
	db        *gorm.DB
	validate  *validator.Validate // 参数校验器
)

// 初始化数据库
func initDB() {
	// MySQL连接信息：替换成你的【用户名/密码/数据库名】
	dsn := "root:123456@tcp(127.0.0.1:3306)/go_user_admin?charset=utf8mb4&parseTime=True&loc=Local"
	// 打开数据库连接，显示SQL日志（方便调试）
	var err error
	db, err = gorm.Open(mysql.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	})
	if err != nil {
		panic("数据库连接失败：" + err.Error())
	}
	// 自动迁移表（不存在则创建，存在则更新结构）
	err = db.AutoMigrate(&model.User{})
	if err != nil {
		panic("表迁移失败：" + err.Error())
	}
}

// 初始化参数校验器
func initValidator() {
	validate = validator.New()
}

// 自定义响应格式，统一接口返回
func response(c *gin.Context, code int, msg string, data interface{}) {
	c.JSON(code, gin.H{
		"code": code,
		"msg":  msg,
		"data": data,
	})
}

// 校验参数中间件
func validateMiddleware(c *gin.Context) {
	// 从上下文获取要校验的参数对象
	obj, ok := c.Get("validateObj")
	if !ok {
		response(c, http.StatusBadRequest, "参数校验失败", nil)
		c.Abort()
		return
	}
	// 校验参数
	if err := validate.Struct(obj); err != nil {
		// 提取校验错误信息
		errMsg := err.(validator.ValidationErrors)[0].Translate(nil)
		response(c, http.StatusBadRequest, errMsg, nil)
		c.Abort()
		return
	}
	c.Next()
}

// JWT鉴权中间件（保护需要登录的接口）
func authMiddleware(c *gin.Context) {
	// 从Header获取token：Bearer <token>
	tokenStr := c.GetHeader("Authorization")
	if tokenStr == "" || len(tokenStr) < 7 {
		response(c, http.StatusUnauthorized, "请先登录", nil)
		c.Abort()
		return
	}
	// 截取真正的token（去掉Bearer 前缀）
	tokenStr = tokenStr[7:]
	// 解析token
	claims, err := model.ParseToken(tokenStr)
	if err != nil {
		response(c, http.StatusUnauthorized, "token无效或已过期", nil)
		c.Abort()
		return
	}
	// 将用户信息存入上下文，供后续接口使用
	c.Set("userID", claims.UserID)
	c.Set("username", claims.Username)
	c.Next()
}

// 注册接口
func register(c *gin.Context) {
	var user model.User
	// 绑定JSON参数到结构体
	if err := c.ShouldBindJSON(&user); err != nil {
		response(c, http.StatusBadRequest, "参数格式错误", nil)
		return
	}
	// 校验参数
	if err := validate.Struct(&user); err != nil {
		errMsg := err.(validator.ValidationErrors)[0].Translate(nil)
		response(c, http.StatusBadRequest, errMsg, nil)
		return
	}
	// 创建用户
	if err := db.Create(&user).Error; err != nil {
		response(c, http.StatusInternalServerError, "注册失败，用户名/手机号已存在", nil)
		return
	}
	// 隐藏密码，返回用户信息
	user.Password = ""
	response(c, http.StatusOK, "注册成功", user)
}

// 登录接口
func login(c *gin.Context) {
	var req struct {
		Username string `json:"username" validate:"required"`
		Password string `json:"password" validate:"required"`
	}
	// 绑定并校验参数
	if err := c.ShouldBindJSON(&req); err != nil {
		response(c, http.StatusBadRequest, "参数格式错误", nil)
		return
	}
	if err := validate.Struct(&req); err != nil {
		errMsg := err.(validator.ValidationErrors)[0].Translate(nil)
		response(c, http.StatusBadRequest, errMsg, nil)
		return
	}
	// 查询用户
	var user model.User
	if err := db.Where("username = ?", req.Username).First(&user).Error; err != nil {
		response(c, http.StatusNotFound, "用户名或密码错误", nil)
		return
	}
	// 实习项目简化：密码明文对比（面试说明“生产环境用bcrypt加密”）
	if user.Password != req.Password {
		response(c, http.StatusNotFound, "用户名或密码错误", nil)
		return
	}
	// 生成JWT令牌
	token, err := model.GenerateToken(user.ID, user.Username)
	if err != nil {
		response(c, http.StatusInternalServerError, "登录失败", nil)
		return
	}
	// 返回token
	response(c, http.StatusOK, "登录成功", gin.H{"token": token})
}

// 获取用户列表（带分页，需要登录）
func getUserList(c *gin.Context) {
	// 获取分页参数：page（页码，默认1）、size（每页条数，默认10）
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	size, _ := strconv.Atoi(c.DefaultQuery("size", "10"))
	offset := (page - 1) * size // 计算偏移量

	// 查询用户列表+总条数
	var users []model.User
	var total int64
	db.Model(&model.User{}).Count(&total)
	db.Limit(size).Offset(offset).Find(&users)

	// 隐藏所有用户密码
	for i := range users {
		users[i].Password = ""
	}

	// 返回分页数据
	response(c, http.StatusOK, "查询成功", gin.H{
		"list":  users,
		"total": total,
		"page":  page,
		"size":  size,
	})
}

// 获取当前登录用户信息（需要登录）
func getCurrentUser(c *gin.Context) {
	// 从上下文获取用户ID（鉴权中间件存入）
	userID, _ := c.Get("userID")
	// 查询用户
	var user model.User
	if err := db.First(&user, userID).Error; err != nil {
		response(c, http.StatusNotFound, "用户不存在", nil)
		return
	}
	// 隐藏密码
	user.Password = ""
	response(c, http.StatusOK, "查询成功", user)
}

// 更新用户信息（需要登录）
func updateUser(c *gin.Context) {
	// 获取路径参数：用户ID
	id, _ := strconv.Atoi(c.Param("id"))
	// 绑定更新参数
	var req model.User
	if err := c.ShouldBindJSON(&req); err != nil {
		response(c, http.StatusBadRequest, "参数格式错误", nil)
		return
	}
	// 只更新允许修改的字段（手机号）
	if err := db.Model(&model.User{}).Where("id = ?", id).Update("Phone", req.Phone).Error; err != nil {
		response(c, http.StatusInternalServerError, "更新失败", nil)
		return
	}
	response(c, http.StatusOK, "更新成功", nil)
}

// 删除用户（需要登录）
func deleteUser(c *gin.Context) {
	// 获取路径参数：用户ID
	id, _ := strconv.Atoi(c.Param("id"))
	// 删除用户（软删除，gorm.Model自带DeleteAt）
	if err := db.Delete(&model.User{}, id).Error; err != nil {
		response(c, http.StatusInternalServerError, "删除失败", nil)
		return
	}
	response(c, http.StatusOK, "删除成功", nil)
}

func main() {
	// 初始化数据库和校验器
	initDB()
	initValidator()

	// 启动Gin服务，发布模式（生产环境用）
	// gin.SetMode(gin.ReleaseMode)
	r := gin.Default()
	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"*"}, // 允许所有域名
		AllowMethods:     []string{"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"*"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))
	// 公开路由（无需登录）
	public := r.Group("/api/v1")
	{
		public.POST("/register", register) // 注册
		public.POST("/login", login)       // 登录
	}

	// 私有路由（需要JWT鉴权）
	private := r.Group("/api/v1")
	private.Use(authMiddleware) // 全局挂载鉴权中间件
	{
		private.GET("/users", getUserList)        // 获取用户列表（分页）
		private.GET("/user/me", getCurrentUser)   // 获取当前用户信息
		private.PUT("/user/:id", updateUser)      // 更新用户信息
		private.DELETE("/user/:id", deleteUser)   // 删除用户
	}

	// 启动服务，监听8080端口
	err := r.Run(":8080")
	if err != nil {
		panic("服务启动失败：" + err.Error())
	}
}
