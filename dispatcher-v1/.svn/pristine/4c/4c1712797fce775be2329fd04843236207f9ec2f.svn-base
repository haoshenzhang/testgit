-- ----------------------------
-- Table structure for `com_user_log`
-- ----------------------------
DROP TABLE IF EXISTS `com_user_log`;
CREATE TABLE `com_user_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '编号',
  `user_id` varchar(20) COLLATE utf8_general_ci NOT NULL DEFAULT '-1' COMMENT '-1,表示匿名用户或者未登录用户，其它则正常为用户工号',
  `user_name` varchar(30) COLLATE utf8_general_ci NOT NULL DEFAULT '匿名用户' COMMENT '操作人用户名',
  `login_ip` varchar(20) COLLATE utf8_general_ci NOT NULL COMMENT '操作人ip',
  `port` int(11) NOT NULL DEFAULT '5000' COMMENT '端口号',
  `url` varchar(255) COLLATE utf8_general_ci NOT NULL COMMENT '操作的url',
  `method` enum('POST','DELETE','PUT','GET') COLLATE utf8_general_ci NOT NULL DEFAULT 'POST' COMMENT '操作的方法',
  `level` enum('ERROR','WARNING','INFO') COLLATE utf8_general_ci NOT NULL DEFAULT 'INFO' COMMENT '操作等级，默认',
  `model` varchar(20) COLLATE utf8_general_ci DEFAULT NULL COMMENT '模块名',
  `operation` varchar(1000) COLLATE utf8_general_ci DEFAULT NULL COMMENT '操作内容，为了方便存储和读取，采用Json字符串形式记录具体的操作内容，例如：{“查询类型”:“值”, “查询名称”:“值”, “公司”:“值”,……….}',
  `create_date` datetime NOT NULL COMMENT '请求时间',
  `update_date` datetime DEFAULT NULL COMMENT '请求完成，记录操作时间',
  `result_code` varchar(20) COLLATE utf8_general_ci DEFAULT NULL COMMENT '放回结果状态',
  `result_msg` varchar(255) COLLATE utf8_general_ci DEFAULT NULL COMMENT '放回结果消息',
  `remark` varchar(500) COLLATE utf8_general_ci DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci COMMENT='用户操作日志表';

-- ----------------------------
-- Table structure for `com_temp_info`
-- ----------------------------
DROP TABLE IF EXISTS `com_temp_info`;
CREATE TABLE `com_temp_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '缓存编号',
  `client_name` varchar(255) NOT NULL,
  `app_token` varchar(255) NOT NULL COMMENT 'app_token，标识，作为project标识当前操作用户身份缓存',
  `call_access_token` varchar(255) DEFAULT NULL COMMENT '针对第三方平台调用传递的access_token',
  `call_client_name` varchar(255) DEFAULT NULL COMMENT '远程调用第三方平台对于的应用名',
  `user` text NOT NULL COMMENT '缓存的当前用户信息，json格式存储',
  `group` text COMMENT '缓存的分组信息，json格式存储',
  `tenant` text COMMENT '缓存的租户信息，json格式存储',
  `other` text COMMENT '缓存的其它信息，json格式存储',
  `created` datetime DEFAULT NULL COMMENT '缓存创建时间',
  PRIMARY KEY (`id`),
  KEY `temp_project_name` (`client_name`),
  KEY `temp_app_token` (`app_token`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT='业务缓存信息表';
