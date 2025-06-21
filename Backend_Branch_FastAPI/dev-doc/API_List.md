# API 开发 Checklist

## 用户认证相关API
- [x] `POST /register` - 用户注册
- [x] `POST /login` - 用户登录
- [x] `POST /logout` - 用户登出
- [ ] `POST /verify-email` - 验证邮箱
- [ ] `POST /forgot-password` - 忘记密码请求

## 用户管理API
### 用户信息
- [ ] `GET ` - 获取用户列表(管理员)
- [ ] `GET /{id}` - 获取特定用户信息
- [ ] `GET /me` - 获取当前用户信息
- [ ] `PUT /{id}` - 更新用户信息
- [ ] `PATCH /{id}/status` - 更新用户状态(管理员)
- [ ] `PATCH /{id}/permission` - 更新用户权限(管理员)
- [ ] `DELETE /{id}` - 删除用户(管理员或自己)

### 用户统计
- [ ] `GET /{id}/stats` - 获取用户统计数据
- [ ] `GET /{id}/activity` - 获取用户活动摘要

## 图片管理API
### 航空图片
- [ ] `POST /aviation-images` - 上传航空图片
- [ ] `GET /aviation-images` - 获取航空图片列表
- [ ] `GET /aviation-images/{id}` - 获取特定航空图片详情
- [ ] `PUT /aviation-images/{id}` - 更新航空图片信息
- [ ] `PATCH /aviation-images/{id}/status` - 更新审核状态(审图员)
- [ ] `DELETE /aviation-images/{id}` - 删除航空图片

### 铁路图片
- [ ] `POST /railway-images` - 上传铁路图片
- [ ] `GET /railway-images` - 获取铁路图片列表
- [ ] `GET /railway-images/{id}` - 获取特定铁路图片详情
- [ ] `PUT /railway-images/{id}` - 更新铁路图片信息
- [ ] `PATCH /railway-images/{id}/status` - 更新审核状态(审图员)
- [ ] `DELETE /railway-images/{id}` - 删除铁路图片

### 图片通用操作
- [ ] `POST /images/{type}/{id}/like` - 点赞图片
- [ ] `DELETE /images/{type}/{id}/like` - 取消点赞
- [ ] `GET /images/{type}/{id}/comments` - 获取图片评论
- [ ] `POST /images/{type}/{id}/comments` - 添加评论

## 机位管理API
- [ ] `POST /spots` - 创建机位信息
- [ ] `GET /spots` - 获取机位列表
- [ ] `GET /spots/{id}` - 获取特定机位详情
- [ ] `PUT /spots/{id}` - 更新机位信息
- [ ] `PATCH /spots/{id}/status` - 更新机位状态
- [ ] `DELETE /spots/{id}` - 删除机位信息

## 勋章管理API
- [ ] `POST /medals` - 授予勋章(管理员)
- [ ] `GET /{id}/medals` - 获取用户勋章列表
- [ ] `GET /medals/{id}` - 获取特定勋章详情
- [ ] `PATCH /medals/{id}/status` - 更新勋章状态(管理员)
- [ ] `DELETE /medals/{id}` - 撤销勋章(管理员)

## 许可证管理API
- [ ] `POST /licenses` - 签发许可证(管理员)
- [ ] `GET /{id}/licenses` - 获取用户许可证列表
- [ ] `GET /licenses/{id}` - 获取特定许可证详情
- [ ] `PATCH /licenses/{id}/status` - 更新许可证状态(管理员)
- [ ] `DELETE /licenses/{id}` - 撤销许可证(管理员)
- [ ] `POST /licenses/{id}/use` - 使用许可证

## 评论管理API
- [ ] `GET /comments/{id}` - 获取评论详情
- [ ] `PUT /comments/{id}` - 更新评论
- [ ] `PATCH /comments/{id}/status` - 更新评论状态
- [ ] `DELETE /comments/{id}` - 删除评论
- [ ] `POST /comments/{id}/like` - 点赞评论
- [ ] `DELETE /comments/{id}/like` - 取消点赞评论
- [ ] `GET /comments/{id}/replies` - 获取评论回复

## 申诉异议API
- [ ] `POST /complaints` - 提交申诉或异议
- [ ] `GET /complaints` - 获取申诉异议列表(管理员)
- [ ] `GET /complaints/{id}` - 获取申诉异议详情
- [ ] `PATCH /complaints/{id}/status` - 处理申诉异议(管理员)
- [ ] `GET /{id}/complaints` - 获取用户申诉异议历史

## 系统管理API
### 系统日志
- [ ] `GET /logs` - 获取系统日志(管理员)
- [ ] `GET /logs/users/{id}` - 获取用户操作日志(管理员)

### 未通过图片
- [ ] `GET /rejected-images` - 获取未通过图片列表(管理员或所有者)
- [ ] `GET /rejected-images/{id}` - 获取未通过图片详情
- [ ] `POST /rejected-images/{id}/resubmit` - 重新提交图片
- [ ] `POST /rejected-images/{id}/appeal` - 对拒绝结果申诉

## 其他实用API
- [ ] `GET /search` - 全局搜索
- [ ] `GET /tags` - 获取热门标签
- [ ] `GET /stats` - 获取系统统计信息
- [ ] `POST /contact` - 联系管理员