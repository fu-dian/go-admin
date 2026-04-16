package model

import (
	"errors"
	"time"

	"github.com/golang-jwt/jwt/v4"
	"gorm.io/gorm"
)

// User 数据模型，映射MySQL表
type User struct {
	gorm.Model        // 自动继承ID/CreateAt/UpdateAt/DeleteAt
	Username string `gorm:"size:32;not null;unique" json:"username" validate:"required,min=3,max=20"` // 用户名，必填，3-20位
	Password string `gorm:"size:64;not null" json:"password" validate:"required,min=6"`               // 密码，必填，至少6位
	Phone    string `gorm:"size:11;unique" json:"phone" validate:"omitempty,len=11"`                  // 手机号，可选，11位
}

// JWT秘钥，实习项目硬编码即可，面试说明“生产环境放配置文件”
var jwtSecret = []byte("go-user-admin-2026")

// 自定义JWT声明
type Claims struct {
	UserID   uint   `json:"user_id"`
	Username string `json:"username"`
	jwt.RegisteredClaims
}

// GenerateToken 生成JWT令牌
func GenerateToken(userID uint, username string) (string, error) {
	// 设置过期时间：24小时
	expireTime := time.Now().Add(24 * time.Hour)
	claims := Claims{
		UserID:   userID,
		Username: username,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(expireTime),
			IssuedAt:  jwt.NewNumericDate(time.Now()),
			Issuer:    "go-user-admin",
		},
	}
	// 用HS256算法生成令牌
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(jwtSecret)
}

// ParseToken 解析JWT令牌
func ParseToken(tokenStr string) (*Claims, error) {
	// 解析令牌
	token, err := jwt.ParseWithClaims(tokenStr, &Claims{}, func(token *jwt.Token) (interface{}, error) {
		return jwtSecret, nil
	})
	if err != nil {
		return nil, err
	}
	// 验证令牌并返回声明
	if claims, ok := token.Claims.(*Claims); ok && token.Valid {
		return claims, nil
	}
	return nil, errors.New("invalid token")
}
