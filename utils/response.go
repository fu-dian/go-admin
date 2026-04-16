package utils

import (
	"github.com/gin-gonic/gin"
	"net/http"
)

type Result struct {
	Code int         `json:"code"`
	Msg  string      `json:"msg"`
	Data interface{} `json:"data"`
}

func Success(c *gin.Context, data interface{}) {
	c.JSON(http.StatusOK, Result{
		Code: 200,
		Msg:  "success",
		Data: data,
	})
}

func Fail(c *gin.Context, msg string) {
	c.JSON(http.StatusOK, Result{
		Code: 500,
		Msg:  msg,
		Data: nil,
	})
}