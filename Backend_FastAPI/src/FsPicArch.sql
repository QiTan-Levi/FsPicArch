-- 创建数据库
CREATE DATABASE IF NOT EXISTS FsPicArch 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE FsPicArch;

-- 用户表 (优化索引和字段)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID，自增主键',
    avatar VARCHAR(255) COMMENT '用户头像URL',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名，唯一',
    password VARCHAR(500) NOT NULL COMMENT '密码，哈西',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱，唯一',
    approved_images_count INT DEFAULT 0 COMMENT '过图数（审核通过的图片数量）',
    likes_received_count INT DEFAULT 0 COMMENT '获赞数',
    uploads_count INT DEFAULT 0 COMMENT '上传数（包括未通过的）',
    views_count INT DEFAULT 0 COMMENT '被浏览数',
    featured_count INT DEFAULT 0 COMMENT '被精选数',
    analysis_score DECIMAL(3,2) COMMENT '分析评分（0-5分）',
    permission_group VARCHAR(50) COMMENT '权限组名称',
    status TINYINT DEFAULT 5 COMMENT '0-禁用 1-正常 2-审图员 3-管理员 4-注销 5-未验证邮箱',
    queue_limit INT DEFAULT 5 COMMENT '列队限制（同时可上传的最大数量）',
    max_image_size INT COMMENT '最大图片尺寸限制（从image_view_level_limit提取）',
    max_image_pixels INT COMMENT '最大图片像素限制（从image_view_level_limit提取）',
    image_view_level_limit JSON COMMENT '图片查看等级限制（详细配置）',
    bio TEXT COMMENT '个人简介',
    personal_watermark VARCHAR(100) COMMENT '个人水印设置',
    inviter_id INT COMMENT '邀请人ID',
    account_level INT DEFAULT 1 COMMENT '账号等级（1-10级）',
    medals_count INT DEFAULT 0 COMMENT '已获得勋章数量',
    notes JSON COMMENT '管理员备注',
    registration_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    last_login DATETIME COMMENT '最后登录时间',
    unique_identifier VARCHAR(100) NOT NULL UNIQUE DEFAULT (UUID()) COMMENT '全局唯一识别符',
    FOREIGN KEY (inviter_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_status (status),
    INDEX idx_account_level (account_level),
    INDEX idx_last_login (last_login)
) COMMENT '用户信息表';

-- 勋章表 (优化索引)
CREATE TABLE medals (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '勋章ID，自增主键',
    user_id INT NOT NULL COMMENT '关联用户ID',
    medal_name VARCHAR(100) NOT NULL COMMENT '勋章名称',
    medal_domain VARCHAR(50) COMMENT '勋章领域（航空/铁路等）',
    medal_type VARCHAR(50) COMMENT '勋章类型',
    medal_unique_code VARCHAR(100) NOT NULL UNIQUE COMMENT '勋章唯一识别码',
    acquisition_date DATE COMMENT '获得日期',
    acquisition_reason TEXT COMMENT '获得原因',
    approver_id INT COMMENT '审批人ID',
    notes TEXT COMMENT '备注信息',
    status TINYINT DEFAULT 1 COMMENT '0-已撤销 1-有效 2-待审核',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (approver_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_medal_user (user_id),
    INDEX idx_medal_status (status)
) COMMENT '用户勋章表';

-- 许可表 (优化索引)
CREATE TABLE licenses (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '许可证ID，自增主键',
    user_id INT NOT NULL COMMENT '关联用户ID',
    license_name VARCHAR(100) NOT NULL COMMENT '许可证名称',
    license_domain VARCHAR(50) COMMENT '许可领域',
    license_type VARCHAR(50) COMMENT '许可类型',
    license_unique_identifier VARCHAR(100) NOT NULL UNIQUE COMMENT '许可证唯一识别符',
    license_key VARCHAR(100) NOT NULL UNIQUE COMMENT '许可证密钥',
    issue_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '签发时间',
    issuer_id INT COMMENT '签发人ID',
    total_uses INT DEFAULT 1 COMMENT '总许可次数',
    remaining_uses INT DEFAULT 1 COMMENT '剩余许可次数',
    last_used DATETIME COMMENT '最近一次使用时间',
    valid_until DATETIME COMMENT '有效期至',
    status TINYINT DEFAULT 1 COMMENT '0-已失效 1-有效 2-暂停',
    notes TEXT COMMENT '备注信息',
    license_content TEXT COMMENT '许可内容详情',
    validity_period VARCHAR(50) COMMENT '有效期描述',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (issuer_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_license_user (user_id),
    INDEX idx_license_status (status),
    INDEX idx_license_valid (valid_until)
) COMMENT '用户许可证表';

-- 机位表 (优化权限存储方式)
CREATE TABLE spots (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '机位ID，自增主键',
    uploader_id INT NOT NULL COMMENT '上传用户ID',
    title VARCHAR(100) NOT NULL COMMENT '机位标题',
    description TEXT COMMENT '机位详细介绍',
    airport VARCHAR(100) COMMENT '所属机场',
    unique_identifier VARCHAR(100) NOT NULL UNIQUE COMMENT '唯一识别码',
    domain VARCHAR(50) COMMENT '领域（航空/铁路等）',
    type_tags JSON COMMENT '类型标签（JSON数组）',
    status TINYINT DEFAULT 0 COMMENT '0-待审核 1-公开 2-私有',
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    notes TEXT COMMENT '备注信息',
    FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_spot_uploader (uploader_id),
    INDEX idx_spot_status (status),
    INDEX idx_spot_domain (domain)
) COMMENT '拍摄机位信息表';


-- 通用图片表
CREATE TABLE images (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '图片ID，自增主键',
    uploader_id INT NOT NULL COMMENT '上传用户ID',
    reviewer_id INT COMMENT '审核人ID',
    domain ENUM('aviation', 'railway') NOT NULL COMMENT '图片领域',
    
    -- 审核相关
    review_comments TEXT COMMENT '审核评语',
    review_time DATETIME COMMENT '审核时间',
    review_modification_log TEXT COMMENT '审核修改日志',
    review_status TINYINT DEFAULT 0 COMMENT '0-待审核 1-已通过 2-已拒绝 3-需修改',
    review_duration INT COMMENT '审核耗时',
    
    -- 图片基本信息
    shooting_time DATETIME COMMENT '拍摄时间',
    upload_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    image_type SET('Airport','Cockpit','Artistic','Ground','Cargo','Special_Livery','Night','Nospecial','Station','Depot','Landscape','Freight', 'To Air', 'To Ground', 'Air to air', 'Dihedral', 'Attack angle', 'Lateral') NOT NULL DEFAULT 'Nospecial',
    weather SET('Sunny','Cloudy','Overcast','Rain','Snow','Fog','Haze','Freezing','Hail') NOT NULL COMMENT '天气状况',
    tags JSON COMMENT '标签组（JSON数组）',
    
    -- 文件信息
    file_size BIGINT COMMENT '文件大小（字节）',
    resolution VARCHAR(20) COMMENT '分辨率（如1920x1080）',
    exposure_parameters JSON COMMENT '曝光参数（JSON格式）',
    file_type ENUM('jpg','jpeg') NOT NULL COMMENT '文件类型',
    
    -- 版权和描述
    copyright_info TEXT COMMENT '版权信息',
    unique_identifier VARCHAR(100) NOT NULL UNIQUE COMMENT '唯一识别符',
    description TEXT COMMENT '图片描述',
    
    -- 位置信息
    location VARCHAR(255) COMMENT '拍摄地点',
    timezone VARCHAR(50) COMMENT '时区',
    
    -- 统计信息
    view_count INT DEFAULT 0 COMMENT '浏览量',
    like_count INT DEFAULT 0 COMMENT '点赞数',
    
    -- 质量评价
    is_featured TINYINT DEFAULT 0 COMMENT '0-普通 1-精选',
    image_quality_level TINYINT COMMENT '图片质量等级（1-5星）',
    rating TINYINT DEFAULT 0 COMMENT '0-未评 1-一星 2-两星 3-三星',
    
    -- 状态
    status TINYINT DEFAULT 1 COMMENT '0-已删除 1-正常 2-隐藏',
    
    -- 领域特有信息
    airline VARCHAR(100) COMMENT '航空公司',
    flight_number VARCHAR(20) COMMENT '航班号',
    aircraft_type VARCHAR(50) COMMENT '机型',
    registration_number VARCHAR(20) COMMENT '注册号',

    train_number VARCHAR(20) COMMENT '车次',
    railway_bureau VARCHAR(50) COMMENT '路局',
    train_type VARCHAR(50) COMMENT '车型',
    
    FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_image_uploader (uploader_id),
    INDEX idx_image_review (review_status),
    INDEX idx_image_domain (domain),
    INDEX idx_image_upload_time (upload_time),
    INDEX idx_image_featured (is_featured),
    INDEX idx_image_quality (image_quality_level)
) COMMENT '通用图片表';

-- 系统日志表
CREATE TABLE system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID，自增主键',
    operator_id INT NOT NULL COMMENT '操作人ID',
    target_type ENUM('user','image','medal','license','spot','comment','complaint') NOT NULL COMMENT '操作目标类型',
    target_id INT NOT NULL COMMENT '操作目标ID',
    operation VARCHAR(50) NOT NULL COMMENT '操作类型',
    operation_detail JSON COMMENT '操作详情（JSON格式）',
    ip_address VARCHAR(50) NOT NULL COMMENT '操作IP地址',
    user_agent VARCHAR(255) COMMENT '用户浏览器/设备信息',
    status ENUM('success','failed','pending') NOT NULL COMMENT '操作状态',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    INDEX idx_operator_id (operator_id),
    INDEX idx_target (target_type, target_id),
    INDEX idx_created_at (created_at),
    INDEX idx_log_status (status)
) COMMENT '系统操作日志表';

-- 点赞表 (优化索引)
CREATE TABLE likes (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '点赞ID，自增主键',
    user_id INT NOT NULL COMMENT '点赞用户ID',
    target_type ENUM('image','comment') NOT NULL COMMENT '点赞目标类型',
    target_id INT NOT NULL COMMENT '点赞目标ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '点赞时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE INDEX idx_user_target (user_id, target_type, target_id),
    INDEX idx_target (target_type, target_id),
    INDEX idx_like_created (created_at)
) COMMENT '用户点赞记录表';

-- 评论表 (优化索引)
CREATE TABLE comments (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '评论ID，自增主键',
    user_id INT NOT NULL COMMENT '评论用户ID',
    target_type ENUM('image','comment') NOT NULL COMMENT '评论目标类型',
    target_id INT NOT NULL COMMENT '评论目标ID',
    content TEXT NOT NULL COMMENT '评论内容',
    status ENUM('published','hidden','deleted') DEFAULT 'published' COMMENT '评论状态',
    like_count INT DEFAULT 0 COMMENT '点赞数',
    reply_count INT DEFAULT 0 COMMENT '回复数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_comment_user (user_id),
    INDEX idx_comment_target (target_type, target_id),
    INDEX idx_comment_status (status),
    INDEX idx_comment_created (created_at),
    INDEX idx_comment_updated (updated_at)
) COMMENT '用户评论表';

-- 未通过图片暂存表 (优化结构)
CREATE TABLE rejected_images (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID，自增主键',
    unique_identifier VARCHAR(100) NOT NULL UNIQUE COMMENT '唯一识别符',
    uploader_id INT NOT NULL COMMENT '上传用户ID',
    reviewer_id INT COMMENT '审核人ID',
    original_image_id INT COMMENT '原始图片ID',
    original_table ENUM('images') COMMENT '原始图片所在表',
    rejection_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '拒绝时间',
    reviewer_modification_log TEXT COMMENT '审核员修改日志',
    shooting_time DATETIME COMMENT '拍摄时间',
    upload_time DATETIME COMMENT '上传时间',
    image_type VARCHAR(50) COMMENT '图片类型',
    tags JSON COMMENT '标签组',
    file_size BIGINT COMMENT '文件大小',
    resolution VARCHAR(20) COMMENT '分辨率',
    exposure_parameters JSON COMMENT '曝光参数',
    copyright_info TEXT COMMENT '版权信息',
    image_data LONGBLOB COMMENT '图片二进制数据',
    description TEXT COMMENT '描述',
    location VARCHAR(255) COMMENT '拍摄地点',
    timezone VARCHAR(50) COMMENT '时区',
    domain ENUM('aviation', 'railway') COMMENT '领域',
    status TINYINT DEFAULT 0 COMMENT '0-已拒绝 1-待审核 2-申诉中',
    domain_specific JSON COMMENT '领域特有信息',
    notes TEXT COMMENT '备注',
    file_type ENUM('jpg', 'jpeg') COMMENT '文件类型',
    FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_rejected_uploader (uploader_id),
    INDEX idx_rejected_status (status),
    INDEX idx_rejected_domain (domain)
) COMMENT '未通过图片暂存表';

-- 申诉异议表 (优化索引)
CREATE TABLE complaints (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '申诉ID，自增主键',
    complaint_type ENUM('appeal', 'objection') NOT NULL COMMENT '申诉类型：appeal-对审核结果申诉 objection-对修改内容异议',
    target_type ENUM('image', 'rejected_image') NOT NULL COMMENT '目标类型',
    target_id INT NOT NULL COMMENT '目标ID',
    target_unique_identifier VARCHAR(100) NOT NULL COMMENT '目标唯一标识符',
    complainant_id INT NOT NULL COMMENT '申诉人ID',
    complaint_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '申诉时间',
    original_review_status TINYINT COMMENT '原始审核状态',
    desired_review_status TINYINT COMMENT '期望审核状态',
    appeal_reason TEXT COMMENT '申诉理由',
    modified_fields JSON COMMENT '被修改的字段列表',
    original_content JSON COMMENT '原始内容',
    objection_reason TEXT COMMENT '异议理由',
    supporting_evidence JSON COMMENT '支持证据',
    status TINYINT DEFAULT 0 COMMENT '0-待处理 1-处理中 2-已解决 3-已驳回',
    handler_id INT COMMENT '处理人ID',
    handling_time DATETIME COMMENT '处理时间',
    handling_result TEXT COMMENT '处理结果',
    handling_notes TEXT COMMENT '处理备注',
    FOREIGN KEY (complainant_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (handler_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_complaint_target (target_type, target_id),
    INDEX idx_complaint_complainant (complainant_id),
    INDEX idx_complaint_status (status),
    INDEX idx_complaint_time (complaint_time)
) COMMENT '用户申诉异议表';

-- 文件表 (优化权限控制)
CREATE TABLE files (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '文件ID，自增主键',
    user_id INT NOT NULL COMMENT '上传用户ID',
    ident_code VARCHAR(64) NOT NULL UNIQUE COMMENT '文件唯一识别码',
    file_name VARCHAR(255) NOT NULL COMMENT '文件名',
    file_path VARCHAR(255) NOT NULL COMMENT '文件存储路径',
    file_type ENUM('aviation', 'railway', 'avatar', 'bg', 'other') NOT NULL COMMENT '文件用途',
    file_info JSON COMMENT '文件信息（JSON格式）',
    related_id INT COMMENT '关联ID（如图片ID等）',
    related_table TEXT COMMENT '关联表',
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    file_tag VARCHAR(100) COMMENT '文件标签',
    is_public BOOLEAN DEFAULT TRUE COMMENT '是否公开',
    status TINYINT DEFAULT 1 COMMENT '0-已删除 1-正常 2-隐藏',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_file_user (user_id),
    INDEX idx_file_type (file_type),
    INDEX idx_file_status (status)
) COMMENT '用户上传文件表';

-- 文件权限表 (新增)
CREATE TABLE file_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '权限ID',
    file_id INT NOT NULL COMMENT '关联文件ID',
    user_id INT COMMENT '关联用户ID（NULL表示权限组）',
    permission_group VARCHAR(50) COMMENT '权限组名称（当user_id为NULL时使用）',
    permission_type ENUM('read', 'write', 'delete', 'share') NOT NULL COMMENT '权限类型',
    granted_by INT COMMENT '授权人ID',
    granted_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '授权时间',
    expires_at DATETIME COMMENT '过期时间',
    FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE KEY uniq_file_user_permission (file_id, user_id, permission_type),
    UNIQUE KEY uniq_file_group_permission (file_id, permission_group, permission_type),
    INDEX idx_file_permission_user (user_id),
    INDEX idx_file_permission_expires (expires_at)
) COMMENT '文件权限表';