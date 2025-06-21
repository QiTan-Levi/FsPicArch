CREATE DATABASE IF NOT EXISTS `FsPicArch` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE FsPicArch;


-- -------------------------
-- 用户信息表
-- -------------------------
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID，自增主键',
    global_uuid CHAR(36) NOT NULL UNIQUE COMMENT '全局唯一UUID（UUIDv4格式）',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名（唯一标识）',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱（验证后可登录）',
    avatar VARCHAR(255) COMMENT '用户头像URL',
    account_level TINYINT UNSIGNED DEFAULT 1 COMMENT '账号等级（1-10级）',
    approved_images_count INT DEFAULT 0 COMMENT '审核通过图片数',
    likes_received_count INT DEFAULT 0 COMMENT '获赞总数',
    uploads_count INT DEFAULT 0 COMMENT '上传图片总数（含未通过）',
    views_count INT DEFAULT 0 COMMENT '被浏览总数',
    featured_count INT DEFAULT 0 COMMENT '被精选图片数',
    analysis_score TINYINT UNSIGNED COMMENT '综合评分（0-100分）',
    permission_group VARCHAR(50) COMMENT '最大权限组名称',
    status TINYINT UNSIGNED DEFAULT 1 COMMENT '0-禁用 1-正常 2-审图员 3-管理员',
    queue_limit SMALLINT UNSIGNED DEFAULT 5 COMMENT '同时可上传最大数量',
    bio TEXT COMMENT '个人简介',
    personal_watermark VARCHAR(100) COMMENT '个人水印设置',
    inviter_id INT COMMENT '邀请人ID',
    medals_count INT DEFAULT 0 COMMENT '已获得勋章数量',
    registration_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    last_login DATETIME COMMENT '最后登录时间',
    CONSTRAINT FK_users_inviter_id FOREIGN KEY (inviter_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_username (username),
    INDEX idx_email (email)
) COMMENT '用户信息表';

-- -------------------------
-- 用户勋章表
-- -------------------------
CREATE TABLE medals (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '勋章ID，自增主键',
    user_id INT NOT NULL COMMENT '关联用户ID',
    medal_name VARCHAR(100) NOT NULL COMMENT '勋章名称',
    medal_domain ENUM('aviation', 'railway', 'system') COMMENT '勋章领域',
    medal_type ENUM('achievement', 'certification') COMMENT '勋章类型',
    global_uuid CHAR(36) NOT NULL UNIQUE COMMENT '全局唯一UUID',
    acquisition_date DATE COMMENT '获得日期',
    acquisition_reason TEXT COMMENT '获得原因',
    approver_id INT COMMENT '审批人ID',
    notes TEXT COMMENT '备注信息',
    status TINYINT UNSIGNED DEFAULT 1 COMMENT '0-已撤销 1-有效 2-待审核',
    CONSTRAINT FK_medals_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT FK_medals_approver_id FOREIGN KEY (approver_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
) COMMENT '用户勋章表';

-- -------------------------
-- 用户许可证表
-- -------------------------
CREATE TABLE licenses (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '许可证ID，自增主键',
    user_id INT NOT NULL COMMENT '关联用户ID',
    license_name VARCHAR(100) NOT NULL COMMENT '许可证名称',
    license_domain ENUM('aviation', 'railway', 'system') COMMENT '许可领域',
    license_type ENUM('permanent', 'temporary') COMMENT '许可类型',
    global_uuid CHAR(36) NOT NULL UNIQUE COMMENT '全局唯一UUID',
    license_key CHAR(32) NOT NULL UNIQUE COMMENT '许可证密钥（MD5生成）',
    issue_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '签发时间',
    issuer_id INT COMMENT '签发人ID',
    total_uses SMALLINT UNSIGNED DEFAULT 1 COMMENT '总许可次数',
    remaining_uses SMALLINT UNSIGNED DEFAULT 1 COMMENT '剩余许可次数',
    last_used DATETIME COMMENT '最近一次使用时间',
    valid_until DATETIME COMMENT '有效期至',
    status TINYINT UNSIGNED DEFAULT 1 COMMENT '0-已失效 1-有效 2-暂停',
    notes TEXT COMMENT '备注信息',
    license_content TEXT COMMENT '许可内容详情',
    validity_period VARCHAR(50) COMMENT '有效期描述',
    CONSTRAINT FK_licenses_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT FK_licenses_issuer_id FOREIGN KEY (issuer_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_license_key (license_key)
) COMMENT '用户许可证表';

-- -------------------------
-- 拍摄机位表
-- -------------------------
CREATE TABLE spots (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '机位ID，自增主键',
    upload_user_id INT NOT NULL COMMENT '上传用户ID',
    spot_name VARCHAR(100) NOT NULL COMMENT '机位名称',
    location VARCHAR(255) NOT NULL COMMENT '机位地点',
    description TEXT COMMENT '机位描述',
    is_public TINYINT UNSIGNED DEFAULT 1 COMMENT '是否公开（0-私有，1-公开）',
    status TINYINT UNSIGNED DEFAULT 1 COMMENT '状态（0-禁用，1-正常）',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    CONSTRAINT FK_spots_upload_user_id FOREIGN KEY (upload_user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_spot_name (spot_name),
    INDEX idx_location (location)
) COMMENT '拍摄机位表';

-- -------------------------
-- 航空图片表
-- -------------------------
CREATE TABLE aviation_images (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '图片ID，自增主键',
    global_uuid CHAR(36) NOT NULL UNIQUE COMMENT '全局唯一UUID',
    uploader_id INT NOT NULL COMMENT '上传用户ID',
    reviewer_id INT COMMENT '审核人ID',
    review_comments TEXT COMMENT '审核评语',
    review_time DATETIME COMMENT '审核时间',
    shooting_time DATETIME COMMENT '拍摄时间',
    upload_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    image_type ENUM('Airport', 'Cockpit', 'Artistic', 'Ground', 'Cargo', 'Special_Livery', 'Night', 'Nospecial') NOT NULL DEFAULT 'Nospecial' COMMENT '图片类型',
    weather ENUM('Sunny', 'Cloudy', 'Overcast', 'Rain', 'Snow', 'Fog', 'Haze', 'Freezing', 'Hail') NOT NULL COMMENT '天气状况',
    tags JSON COMMENT '标签组（JSON数组）',
    file_size BIGINT COMMENT '文件大小（字节）',
    resolution VARCHAR(20) COMMENT '分辨率（如1920x1080）',
    exposure_parameters JSON COMMENT '曝光参数（JSON格式）',
    copyright_info TEXT COMMENT '版权信息',
    description TEXT COMMENT '图片描述',
    location VARCHAR(255) COMMENT '拍摄地点',
    timezone VARCHAR(50) COMMENT '时区',
    review_status TINYINT UNSIGNED DEFAULT 0 COMMENT '0-待审核 1-已通过 2-已拒绝 3-需修改',
    is_featured TINYINT UNSIGNED DEFAULT 0 COMMENT '0-普通 1-精选',
    image_quality_level TINYINT UNSIGNED COMMENT '质量等级（1-5星）',
    rating TINYINT UNSIGNED DEFAULT 0 COMMENT '评分（0-未评，1-3星）',
    view_count INT DEFAULT 0 COMMENT '浏览量',
    review_duration INT COMMENT '审核耗时（秒）',
    required_permission VARCHAR(50) COMMENT '查看所需权限等级',
    status TINYINT UNSIGNED DEFAULT 1 COMMENT '0-已删除 1-正常 2-隐藏',
    airline VARCHAR(100) COMMENT '航空公司',
    flight_number VARCHAR(20) COMMENT '航班号',
    aircraft_type VARCHAR(50) COMMENT '机型',
    registration_number VARCHAR(20) COMMENT '注册号',
    CONSTRAINT FK_aviation_uploader_id FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT FK_aviation_reviewer_id FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_uploader_id (uploader_id),
    INDEX idx_review_status (review_status),
    INDEX idx_is_featured (is_featured)
) COMMENT '航空图片表';

-- -------------------------
-- 铁路图片表
-- -------------------------
CREATE TABLE railway_images (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '图片ID，自增主键',
    global_uuid CHAR(36) NOT NULL UNIQUE COMMENT '全局唯一UUID',
    uploader_id INT NOT NULL COMMENT '上传用户ID',
    reviewer_id INT COMMENT '审核人ID',
    review_comments TEXT COMMENT '审核评语',
    review_time DATETIME COMMENT '审核时间',
    shooting_time DATETIME COMMENT '拍摄时间',
    upload_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    image_type ENUM('Station', 'Depot', 'Artistic', 'Landscape', 'Freight', 'Special_Livery', 'Night', 'Nospecial') NOT NULL DEFAULT 'Nospecial' COMMENT '图片类型',
    weather ENUM('Sunny', 'Cloudy', 'Overcast', 'Rain', 'Snow', 'Fog', 'Haze', 'Freezing', 'Hail') NOT NULL COMMENT '天气状况',
    tags JSON COMMENT '标签组（JSON数组）',
    file_size BIGINT COMMENT '文件大小（字节）',
    resolution VARCHAR(20) COMMENT '分辨率（如1920x1080）',
    exposure_parameters JSON COMMENT '曝光参数（JSON格式）',
    copyright_info TEXT COMMENT '版权信息',
    description TEXT COMMENT '图片描述',
    location VARCHAR(255) COMMENT '拍摄地点',
    timezone VARCHAR(50) COMMENT '时区',
    review_status TINYINT UNSIGNED DEFAULT 0 COMMENT '0-待审核 1-已通过 2-已拒绝 3-需修改',
    is_featured TINYINT UNSIGNED DEFAULT 0 COMMENT '0-普通 1-精选',
    image_quality_level TINYINT UNSIGNED COMMENT '质量等级（1-5星）',
    rating TINYINT UNSIGNED DEFAULT 0 COMMENT '评分（0-未评，1-3星）',
    view_count INT DEFAULT 0 COMMENT '浏览量',
    review_duration INT COMMENT '审核耗时（秒）',
    required_permission VARCHAR(50) COMMENT '查看所需权限等级',
    status TINYINT UNSIGNED DEFAULT 1 COMMENT '0-已删除 1-正常 2-隐藏',
    train_number VARCHAR(20) COMMENT '车次',
    railway_bureau VARCHAR(50) COMMENT '路局',
    train_type VARCHAR(50) COMMENT '车型',
    CONSTRAINT FK_railway_uploader_id FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT FK_railway_reviewer_id FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_uploader_id (uploader_id),
    INDEX idx_review_status (review_status),
    INDEX idx_is_featured (is_featured)
) COMMENT '铁路图片表';


### **四、互动与审核表**
-- -------------------------
-- 点赞记录表
-- -------------------------
CREATE TABLE likes (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '点赞ID，自增主键',
    user_id INT NOT NULL COMMENT '点赞用户ID',
    target_type ENUM('image', 'comment') NOT NULL COMMENT '点赞目标类型',
    target_id INT NOT NULL COMMENT '点赞目标ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '点赞时间',
    global_uuid CHAR(36) NOT NULL UNIQUE COMMENT '全局唯一UUID',
    CONSTRAINT FK_likes_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY idx_user_target (user_id, target_type, target_id),
    INDEX idx_target_type (target_type, target_id)
) COMMENT '用户点赞记录表';

-- -------------------------
-- 评论表
-- -------------------------
CREATE TABLE comments (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '评论ID，自增主键',
    user_id INT NOT NULL COMMENT '评论用户ID',
    target_type ENUM('image', 'comment') NOT NULL COMMENT '评论目标类型',
    target_id INT NOT NULL COMMENT '评论目标ID',
    parent_id INT COMMENT '父评论ID（回复时关联）',
    content TEXT NOT NULL COMMENT '评论内容',
    status ENUM('published', 'hidden', 'deleted') DEFAULT 'published' COMMENT '评论状态',
    like_count INT DEFAULT 0 COMMENT '点赞数',
    reply_count INT DEFAULT 0 COMMENT '回复数',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    global_uuid CHAR(36) NOT NULL UNIQUE COMMENT '全局唯一UUID',
    CONSTRAINT FK_comments_user_id FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_target_type (target_type, target_id),
    INDEX idx_parent_id (parent_id)
) COMMENT '用户评论表';

-- -------------------------
-- 未通过图片暂存表
-- -------------------------
CREATE TABLE rejected_images (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID，自增主键',
    global_uuid CHAR(36) NOT NULL UNIQUE COMMENT '全局唯一UUID',
    uploader_id INT NOT NULL COMMENT '上传用户ID',
    reviewer_id INT COMMENT '审核人ID',
    original_image_id INT COMMENT '原始图片ID',
    original_table ENUM('aviation_images', 'railway_images') COMMENT '原始表名',
    rejection_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '拒绝时间',
    reviewer_modification_log TEXT COMMENT '审核修改日志',
    shooting_time DATETIME COMMENT '拍摄时间',
    upload_time DATETIME COMMENT '上传时间',
    image_type VARCHAR(50) COMMENT '图片类型',
    tags JSON COMMENT '标签组',
    file_size BIGINT COMMENT '文件大小',
    resolution VARCHAR(20) COMMENT '分辨率',
    exposure_parameters JSON COMMENT '曝光参数',
    copyright_info TEXT COMMENT '版权信息',
    description TEXT COMMENT '图片描述',
    location VARCHAR(255) COMMENT '拍摄地点',
    timezone VARCHAR(50) COMMENT '时区',
    required_permission VARCHAR(50) COMMENT '查看权限等级',
    status TINYINT UNSIGNED DEFAULT 0 COMMENT '0-已拒绝 1-待审核 2-申诉中',
    -- 领域相关字段（通过外键关联，非冗余存储）
    domain ENUM('aviation', 'railway') COMMENT '领域',
    notes TEXT COMMENT '备注',
    -- 外键
    CONSTRAINT FK_rejected_uploader_id FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT FK_rejected_reviewer_id FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_uploader_id (uploader_id),
    INDEX idx_domain (domain),
    INDEX idx_status (status)
) COMMENT '未通过图片暂存表';

-- -------------------------
-- 申诉异议表
-- -------------------------
CREATE TABLE complaints (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '申诉ID，自增主键',
    complaint_type ENUM('appeal', 'objection') NOT NULL COMMENT '申诉类型：appeal-对审核结果申诉 objection-对修改内容异议',
    target_type ENUM('aviation_image', 'railway_image', 'rejected_image') NOT NULL COMMENT '目标类型',
    target_id INT NOT NULL COMMENT '目标ID',
    target_uuid CHAR(36) NOT NULL COMMENT '目标全局唯一UUID',
    complainant_id INT NOT NULL COMMENT '申诉人ID',
    complaint_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '申诉时间',
    
    -- 申诉（appeal）特有字段
    original_review_status TINYINT UNSIGNED COMMENT '原始审核状态（关联图片的审核状态）',
    desired_review_status TINYINT UNSIGNED COMMENT '期望审核状态（如通过/拒绝）',
    appeal_reason TEXT COMMENT '申诉理由（需具体说明）',
    
    -- 异议（objection）特有字段
    modified_fields JSON COMMENT '被修改的字段列表（JSON格式，如["image_type", "tags"]）',
    original_content JSON COMMENT '原始内容（修改前的字段值）',
    objection_reason TEXT COMMENT '异议理由（针对修改内容的质疑）',
    
    -- 通用字段
    supporting_evidence JSON COMMENT '支持证据（如图片、文档URL的JSON数组）',
    status TINYINT UNSIGNED DEFAULT 0 COMMENT '0-待处理 1-处理中 2-已解决 3-已驳回',
    handler_id INT COMMENT '处理人ID（审核员或管理员）',
    handling_time DATETIME COMMENT '处理时间',
    handling_result TEXT COMMENT '处理结果（如维持原判/撤销审核）',
    handling_notes TEXT COMMENT '处理备注（内部沟通记录）',
    global_uuid CHAR(36) NOT NULL UNIQUE COMMENT '申诉全局唯一UUID',
    
    -- 外键约束
    CONSTRAINT FK_complaints_complainant_id FOREIGN KEY (complainant_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT FK_complaints_handler_id FOREIGN KEY (handler_id) REFERENCES users(id) ON DELETE SET NULL,
    
    -- 索引优化
    INDEX idx_complaint_type_status (complaint_type, status), -- 按类型和状态快速查询
    INDEX idx_target_type_id (target_type, target_id),         -- 按目标类型和ID检索
    INDEX idx_complainant_id (complainant_id),                 -- 按申诉人查询
    INDEX idx_global_uuid (global_uuid)                       -- 按UUID快速定位
) COMMENT '用户申诉异议表';

CREATE TABLE verification_codes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    code VARCHAR(6) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('未使用', '已使用', '已过期') DEFAULT '未使用',
    expiration_time TIMESTAMP NULL DEFAULT NULL,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) COMMENT '用户验证码表';

DELIMITER //
-- 航空图片触发器（已完成）
CREATE TRIGGER after_aviation_image_approval
AFTER UPDATE ON aviation_images
FOR EACH ROW
BEGIN
    -- 审核通过时更新用户统计
    IF NEW.review_status = 1 AND OLD.review_status != 1 THEN
        UPDATE users 
        SET approved_images_count = approved_images_count + 1,
            uploads_count = uploads_count + 1
        WHERE id = NEW.uploader_id;
    END IF;
    
    -- 标记为精选时更新用户精选数
    IF NEW.is_featured = 1 AND OLD.is_featured = 0 THEN
        UPDATE users 
        SET featured_count = featured_count + 1
        WHERE id = NEW.uploader_id;
    END IF;
END//

-- 铁路图片触发器（复用逻辑，仅需修改表名）
CREATE TRIGGER after_railway_image_approval
AFTER UPDATE ON railway_images
FOR EACH ROW
BEGIN
    IF NEW.review_status = 1 AND OLD.review_status != 1 THEN
        UPDATE users 
        SET approved_images_count = approved_images_count + 1,
            uploads_count = uploads_count + 1
        WHERE id = NEW.uploader_id;
    END IF;
    
    IF NEW.is_featured = 1 AND OLD.is_featured = 0 THEN
        UPDATE users 
        SET featured_count = featured_count + 1
        WHERE id = NEW.uploader_id;
    END IF;
END//
DELIMITER ;

DELIMITER //
-- 新增勋章时更新用户勋章数
CREATE TRIGGER after_medal_insert
AFTER INSERT ON medals
FOR EACH ROW
BEGIN
    UPDATE users 
    SET medals_count = medals_count + 1
    WHERE id = NEW.user_id;
END//

-- 删除勋章时减少用户勋章数
CREATE TRIGGER after_medal_delete
AFTER DELETE ON medals
FOR EACH ROW
BEGIN
    UPDATE users 
    SET medals_count = medals_count - 1
    WHERE id = OLD.user_id;
END//
DELIMITER ;

CREATE VIEW vw_all_images AS
SELECT 
    id,
    global_uuid,
    uploader_id,
    reviewer_id,
    shooting_time,
    upload_time,
    image_type,
    weather,
    tags,
    description,
    location,
    'aviation' AS domain, -- 领域标识
    airline,
    flight_number,
    aircraft_type,
    registration_number,
    NULL AS train_number,
    NULL AS railway_bureau,
    NULL AS train_type
FROM aviation_images
UNION ALL
SELECT 
    id,
    global_uuid,
    uploader_id,
    reviewer_id,
    shooting_time,
    upload_time,
    image_type,
    weather,
    tags,
    description,
    location,
    'railway' AS domain, -- 领域标识
    NULL AS airline,
    NULL AS flight_number,
    NULL AS aircraft_type,
    NULL AS registration_number,
    train_number,
    railway_bureau,
    train_type
FROM railway_images;

CREATE VIEW vw_user_statistics AS
SELECT 
    u.id,
    u.username,
    u.account_level,
    u.approved_images_count,
    u.likes_received_count,
    u.uploads_count,
    u.views_count,
    u.featured_count,
    m.medals_count
FROM users u
LEFT JOIN (
    SELECT user_id, COUNT(*) AS medals_count
    FROM medals
    GROUP BY user_id
) m ON u.id = m.user_id;