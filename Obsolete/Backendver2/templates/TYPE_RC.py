# 通知类型与主题映射
TYPE_SUBJECTS = {
    "VERICODE": "您正获取的Byinfo验证码",
    "LOGINREMIND": "Byinfo账号登录通知",
    "REVIEWRESULT": "您在Byinfo PicSvc上传的作品审核结果",
    "MEDALLICENSECHANGE": "Byinfo账号变更提醒",
    "COMPLAINTRESULT": "Byinfo对您的申诉/异议处理结果",
    "LICENSEUSAGEREMINDER": "Byinfo许可证使用提醒",
    "SECURITYALERT": "Byinfo账号安全警告",
}

# 通知类型与必填参数映射
TYPE_PARAMS = {
    "VERICODE": [
        "code",               # 验证码内容
        "user_id",            # 用户唯一标识
        "expire_time",        # 有效期
        "current_time"         # 变更时间戳
    ],
    "LOGINREMIND": [
        "username",           # 用户名
        "time",               # 登录时间
        "location",           # 登录地点
        "device_info",        # 设备信息
        "ip_address",         # IP地址
        "current_time"         # 变更时间戳
    ],
    "REVIEWRESULT": [
        "image_title",        # 图片标题
        "review_status",      # 审核状态
        "comments",           # 审核意见
        "submit_time",        # 提交时间
        "current_time"         # 变更时间戳
    ],
    "MEDALLICENSECHANGE": [
        "username",           # 用户名
        "item_type",          # 权益类型
        "item_name",          # 权益名称
        "status",             # 变更状态
        "current_time"         # 变更时间戳
    ],
    "COMPLAINTRESULT": [
        "complaint_id",       # 投诉单号
        "result",             # 处理结果
        "handling_notes",     # 处理备注
        "handler_name",       # 处理人姓名
        "current_time"         # 变更时间戳
    ],
    "LICENSEUSAGEREMINDER": [
        "license_name",       # 许可证名称
        "remaining_uses",     # 剩余次数
        "valid_until",        # 有效期至
        "total_uses",         # 总使用次数
        "current_time"         # 变更时间戳
    ],
    "SECURITYALERT": [
        "alert_type",         # 警报类型
        "details",            # 警报详情
        "occur_time",         # 发生时间
        "current_time"         # 变更时间戳
    ]
}