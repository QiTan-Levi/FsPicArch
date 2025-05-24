-- 创建数据库
CREATE DATABASE IF NOT EXISTS FsPicArch 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE aviation_railway_platform;

-- 用户表
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID，自增主键',
    avatar VARCHAR(255) COMMENT '用户头像URL',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名，唯一',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱，唯一',
    approved_images_count INT DEFAULT 0 COMMENT '过图数（审核通过的图片数量）',
    likes_received_count INT DEFAULT 0 COMMENT '获赞数',
    uploads_count INT DEFAULT 0 COMMENT '上传数（包括未通过的）',
    views_count INT DEFAULT 0 COMMENT '被浏览数',
    featured_count INT DEFAULT 0 COMMENT '被精选数',
    analysis_score DECIMAL(3,2) COMMENT '分析评分（0-5分）',
    permission_group VARCHAR(50) COMMENT '权限组名称',
    status TINYINT DEFAULT 1 COMMENT '0-禁用 1-正常 2-审图员 3-管理员',
    queue_limit INT DEFAULT 5 COMMENT '列队限制（同时可上传的最大数量）',
    image_view_level_limit JSON COMMENT '图片查看等级限制（包含文件大小、像素等限制）',
    bio TEXT COMMENT '个人简介',
    personal_watermark VARCHAR(100) COMMENT '个人水印设置',
    inviter_id INT COMMENT '邀请人ID',
    account_level INT DEFAULT 1 COMMENT '账号等级（1-10级）',
    medals_count INT DEFAULT 0 COMMENT '已获得勋章数量',
    notes TEXT COMMENT '管理员备注',
    registration_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
    last_login DATETIME COMMENT '最后登录时间',
    unique_identifier VARCHAR(100) NOT NULL UNIQUE COMMENT '全局唯一识别符',
    FOREIGN KEY (inviter_id) REFERENCES users(id) ON DELETE SET NULL
) COMMENT '用户信息表';

-- 勋章表
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
    FOREIGN KEY (approver_id) REFERENCES users(id) ON DELETE SET NULL
) COMMENT '用户勋章表';

-- 许可表
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
    FOREIGN KEY (issuer_id) REFERENCES users(id) ON DELETE SET NULL
) COMMENT '用户许可证表';

-- 机位表
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
    view_permission_group VARCHAR(50) COMMENT '查看权限组',
    allowed_viewer_ids JSON COMMENT '被允许查看的用户ID列表（JSON数组）',
    upload_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    notes TEXT COMMENT '备注信息',
    FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE CASCADE
) COMMENT '拍摄机位信息表';

-- 航空图片表
CREATE TABLE aviation_images (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '图片ID，自增主键',
    uploader_id INT NOT NULL COMMENT '上传用户ID',
    reviewer_id INT COMMENT '审核人ID',
    review_comments TEXT COMMENT '审核评语',
    review_time DATETIME COMMENT '审核时间',
    review_modification_log TEXT COMMENT '审核修改日志',
    shooting_time DATETIME COMMENT '拍摄时间',
    upload_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    
    -- 图片类型
    image_type SET('Airport', 'Cockpit', 'Artistic', 'Ground', 'Cargo', 'Special_Livery', 'Night', 'Nospecial') NOT NULL DEFAULT 'Nospecial' COMMENT '图片类型',
    
    -- 天气状况
    weather SET('Sunny', 'Cloudy', 'Overcast', 'Rain', 'Snow', 'Fog', 'Haze', 'Freezing', 'Hail') NOT NULL COMMENT '天气状况',
    
    tags JSON COMMENT '标签组（JSON数组）',
    file_size BIGINT COMMENT '文件大小（字节）',
    resolution VARCHAR(20) COMMENT '分辨率（如1920x1080）',
    exposure_parameters JSON COMMENT '曝光参数（JSON格式）',
    copyright_info TEXT COMMENT '版权信息',
    unique_identifier VARCHAR(100) NOT NULL UNIQUE COMMENT '唯一识别符',
    description TEXT COMMENT '图片描述',
    location VARCHAR(255) COMMENT '拍摄地点',
    notes TEXT COMMENT '备注信息',
    last_update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    timezone VARCHAR(50) COMMENT '时区',
    review_status TINYINT DEFAULT 0 COMMENT '0-待审核 1-已通过 2-已拒绝 3-需修改',
    is_featured TINYINT DEFAULT 0 COMMENT '0-普通 1-精选',
    image_quality_level TINYINT COMMENT '图片质量等级（1-5星）',
    rating TINYINT DEFAULT 0 COMMENT '0-未评 1-一星 2-两星 3-三星',
    view_count INT DEFAULT 0 COMMENT '浏览量',
    review_duration INT COMMENT '审核耗时（秒）',
    required_permission VARCHAR(50) COMMENT '查看所需权限',
    status TINYINT DEFAULT 1 COMMENT '0-已删除 1-正常 2-隐藏',
    airline VARCHAR(100) COMMENT '航空公司',
    flight_number VARCHAR(20) COMMENT '航班号',
    aircraft_type VARCHAR(50) COMMENT '机型',
    registration_number VARCHAR(20) COMMENT '注册号',
    file_type ENUM('jpg', 'jpeg') NOT NULL COMMENT '文件类型',
    
    FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL
) COMMENT '航空图片表';

-- 铁路图片表
CREATE TABLE railway_images (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '图片ID，自增主键',
    uploader_id INT NOT NULL COMMENT '上传用户ID',
    reviewer_id INT COMMENT '审核人ID',
    review_comments TEXT COMMENT '审核评语',
    review_time DATETIME COMMENT '审核时间',
    review_modification_log TEXT COMMENT '审核修改日志',
    shooting_time DATETIME COMMENT '拍摄时间',
    upload_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    
    -- 图片类型
    image_type SET('Station', 'Depot', 'Artistic', 'Landscape', 'Freight', 'Special_Livery', 'Night', 'Nospecial') NOT NULL DEFAULT 'Nospecial' COMMENT '图片类型',
    
    -- 天气状况
    weather SET('Sunny', 'Cloudy', 'Overcast', 'Rain', 'Snow', 'Fog', 'Haze', 'Freezing', 'Hail') NOT NULL COMMENT '天气状况',
    
    tags JSON COMMENT '标签组（JSON数组）',
    file_size BIGINT COMMENT '文件大小（字节）',
    resolution VARCHAR(20) COMMENT '分辨率（如1920x1080）',
    exposure_parameters JSON COMMENT '曝光参数（JSON格式）',
    copyright_info TEXT COMMENT '版权信息',
    unique_identifier VARCHAR(100) NOT NULL UNIQUE COMMENT '唯一识别符',
    description TEXT COMMENT '图片描述',
    location VARCHAR(255) COMMENT '拍摄地点',
    notes TEXT COMMENT '备注信息',
    last_update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    timezone VARCHAR(50) COMMENT '时区',
    review_status TINYINT DEFAULT 0 COMMENT '0-待审核 1-已通过 2-已拒绝 3-需修改',
    is_featured TINYINT DEFAULT 0 COMMENT '0-普通 1-精选',
    image_quality_level TINYINT COMMENT '图片质量等级（1-5星）',
    rating TINYINT DEFAULT 0 COMMENT '0-未评 1-一星 2-两星 3-三星',
    view_count INT DEFAULT 0 COMMENT '浏览量',
    review_duration INT COMMENT '审核耗时（秒）',
    required_permission VARCHAR(50) COMMENT '查看所需权限',
    status TINYINT DEFAULT 1 COMMENT '0-已删除 1-正常 2-隐藏',
    train_number VARCHAR(20) COMMENT '车次',
    railway_bureau VARCHAR(50) COMMENT '路局',
    train_type VARCHAR(50) COMMENT '车型',
    file_type ENUM('jpg', 'jpeg') NOT NULL COMMENT '文件类型',
    
    FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL
) COMMENT '铁路图片表';

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
    
    FOREIGN KEY (operator_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_operator_id (operator_id),
    INDEX idx_target (target_type, target_id),
    INDEX idx_created_at (created_at)
) COMMENT '系统操作日志表';

-- 点赞表
CREATE TABLE likes (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '点赞ID，自增主键',
    user_id INT NOT NULL COMMENT '点赞用户ID',
    target_type ENUM('image','comment') NOT NULL COMMENT '点赞目标类型',
    target_id INT NOT NULL COMMENT '点赞目标ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '点赞时间',
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE INDEX idx_user_target (user_id, target_type, target_id),
    INDEX idx_target (target_type, target_id)
) COMMENT '用户点赞记录表';

-- 评论表
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
    INDEX idx_user_id (user_id),
    INDEX idx_target (target_type, target_id),
    INDEX idx_created_at (created_at)
) COMMENT '用户评论表';

-- 未通过图片暂存表
CREATE TABLE rejected_images (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID，自增主键',
    unique_identifier VARCHAR(100) NOT NULL UNIQUE COMMENT '唯一识别符',
    uploader_id INT NOT NULL COMMENT '上传用户ID',
    reviewer_id INT COMMENT '审核人ID',
    original_image_id INT COMMENT '原始图片ID',
    original_table ENUM('aviation_images', 'railway_images') COMMENT '原始图片所在表',
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
    required_permission VARCHAR(50) COMMENT '查看所需权限',
    status TINYINT DEFAULT 0 COMMENT '0-已拒绝 1-待审核 2-申诉中',
    
    -- 航空特有字段
    airline VARCHAR(100) COMMENT '航空公司',
    flight_number VARCHAR(20) COMMENT '航班号',
    aircraft_type VARCHAR(50) COMMENT '机型',
    registration_number VARCHAR(20) COMMENT '注册号',
    
    -- 铁路特有字段
    train_number VARCHAR(20) COMMENT '车次',
    railway_bureau VARCHAR(50) COMMENT '路局',
    train_type VARCHAR(50) COMMENT '车型',
    
    -- 通用字段
    domain ENUM('aviation', 'railway') COMMENT '领域',
    notes TEXT COMMENT '备注',
    file_type ENUM('jpg', 'jpeg') COMMENT '文件类型',
    
    FOREIGN KEY (uploader_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE SET NULL
) COMMENT '未通过图片暂存表';

-- 申诉异议表
CREATE TABLE complaints (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '申诉ID，自增主键',
    complaint_type ENUM('appeal', 'objection') NOT NULL COMMENT '申诉类型：appeal-对审核结果申诉 objection-对修改内容异议',
    target_type ENUM('aviation_image', 'railway_image', 'rejected_image') NOT NULL COMMENT '目标类型',
    target_id INT NOT NULL COMMENT '目标ID',
    target_unique_identifier VARCHAR(100) NOT NULL COMMENT '目标唯一标识符',
    complainant_id INT NOT NULL COMMENT '申诉人ID',
    complaint_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '申诉时间',
    
    -- 申诉特有字段
    original_review_status TINYINT COMMENT '原始审核状态',
    desired_review_status TINYINT COMMENT '期望审核状态',
    appeal_reason TEXT COMMENT '申诉理由',
    
    -- 异议特有字段
    modified_fields JSON COMMENT '被修改的字段列表',
    original_content JSON COMMENT '原始内容',
    objection_reason TEXT COMMENT '异议理由',
    
    -- 通用字段
    supporting_evidence JSON COMMENT '支持证据',
    status TINYINT DEFAULT 0 COMMENT '0-待处理 1-处理中 2-已解决 3-已驳回',
    handler_id INT COMMENT '处理人ID',
    handling_time DATETIME COMMENT '处理时间',
    handling_result TEXT COMMENT '处理结果',
    handling_notes TEXT COMMENT '处理备注',
    
    FOREIGN KEY (complainant_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (handler_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_target (target_type, target_id),
    INDEX idx_complainant (complainant_id),
    INDEX idx_status (status)
) COMMENT '用户申诉异议表';

-- 创建触发器：更新用户统计数据
DELIMITER //
CREATE TRIGGER after_aviation_image_approval
AFTER UPDATE ON aviation_images
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

-- 创建触发器：更新勋章数量
DELIMITER //
CREATE TRIGGER after_medal_insert
AFTER INSERT ON medals
FOR EACH ROW
BEGIN
    UPDATE users 
    SET medals_count = medals_count + 1
    WHERE id = NEW.user_id;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER after_medal_delete
AFTER DELETE ON medals
FOR EACH ROW
BEGIN
    UPDATE users 
    SET medals_count = medals_count - 1
    WHERE id = OLD.user_id;
END//
DELIMITER ;

-- 创建触发器：图片被拒绝时自动复制到暂存表
DELIMITER //
CREATE TRIGGER after_aviation_image_rejection
AFTER UPDATE ON aviation_images
FOR EACH ROW
BEGIN
    IF NEW.review_status = 2 AND OLD.review_status != 2 THEN
        INSERT INTO rejected_images (
            unique_identifier, uploader_id, reviewer_id, original_image_id, original_table,
            rejection_time, reviewer_modification_log, shooting_time, upload_time,
            image_type, tags, file_size, resolution, exposure_parameters, copyright_info,
            description, location, timezone, required_permission, status,
            airline, flight_number, aircraft_type, registration_number, domain, notes, file_type
        )
        SELECT 
            CONCAT('REJ-', NEW.unique_identifier), NEW.uploader_id, NEW.reviewer_id, NEW.id, 'aviation_images',
            NOW(), NEW.review_modification_log, NEW.shooting_time, NEW.upload_time,
            NEW.image_type, NEW.tags, NEW.file_size, NEW.resolution, NEW.exposure_parameters, NEW.copyright_info,
            NEW.description, NEW.location, NEW.timezone, NEW.required_permission, 0,
            NEW.airline, NEW.flight_number, NEW.aircraft_type, NEW.registration_number, 'aviation', NEW.notes, NEW.file_type
        FROM aviation_images WHERE id = NEW.id;
    END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER after_railway_image_rejection
AFTER UPDATE ON railway_images
FOR EACH ROW
BEGIN
    IF NEW.review_status = 2 AND OLD.review_status != 2 THEN
        INSERT INTO rejected_images (
            unique_identifier, uploader_id, reviewer_id, original_image_id, original_table,
            rejection_time, reviewer_modification_log, shooting_time, upload_time,
            image_type, tags, file_size, resolution, exposure_parameters, copyright_info,
            description, location, timezone, required_permission, status,
            train_number, railway_bureau, train_type, domain, notes, file_type
        )
        SELECT 
            CONCAT('REJ-', NEW.unique_identifier), NEW.uploader_id, NEW.reviewer_id, NEW.id, 'railway_images',
            NOW(), NEW.review_modification_log, NEW.shooting_time, NEW.upload_time,
            NEW.image_type, NEW.tags, NEW.file_size, NEW.resolution, NEW.exposure_parameters, NEW.copyright_info,
            NEW.description, NEW.location, NEW.timezone, NEW.required_permission, 0,
            NEW.train_number, NEW.railway_bureau, NEW.train_type, 'railway', NEW.notes, NEW.file_type
        FROM railway_images WHERE id = NEW.id;
    END IF;
END//
DELIMITER ;

-- 创建视图：用户活动摘要
CREATE VIEW user_activity_summary AS
SELECT 
    u.id,
    u.username,
    u.approved_images_count,
    u.likes_received_count,
    u.uploads_count,
    u.views_count,
    u.featured_count,
    COUNT(DISTINCT m.id) AS medals_count,
    COUNT(DISTINCT l.id) AS licenses_count,
    COUNT(DISTINCT s.id) AS spots_count,
    u.registration_time,
    u.last_login
FROM 
    users u
LEFT JOIN 
    medals m ON u.id = m.user_id AND m.status = 1
LEFT JOIN 
    licenses l ON u.id = l.user_id AND l.status = 1
LEFT JOIN 
    spots s ON u.id = s.uploader_id AND s.status = 1
GROUP BY 
    u.id;

-- 创建视图：待处理的申诉异议
CREATE VIEW pending_complaints AS
SELECT 
    c.id,
    c.complaint_type,
    c.target_type,
    c.target_id,
    c.target_unique_identifier,
    c.complaint_time,
    u.username AS complainant,
    CASE 
        WHEN c.complaint_type = 'appeal' THEN CONCAT('申诉: 从状态', c.original_review_status, '改为', c.desired_review_status)
        WHEN c.complaint_type = 'objection' THEN '异议: 对审核修改内容不满'
    END AS complaint_summary,
    c.status,
    h.username AS handler
FROM 
    complaints c
JOIN 
    users u ON c.complainant_id = u.id
LEFT JOIN 
    users h ON c.handler_id = h.id
WHERE 
    c.status IN (0, 1);