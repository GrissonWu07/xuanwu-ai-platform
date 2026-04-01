package xuanwu.modules.sys.dao;

import org.apache.ibatis.annotations.Mapper;

import xuanwu.common.dao.BaseDao;
import xuanwu.modules.sys.entity.SysUserEntity;

/**
 * 系统用户
 */
@Mapper
public interface SysUserDao extends BaseDao<SysUserEntity> {

}