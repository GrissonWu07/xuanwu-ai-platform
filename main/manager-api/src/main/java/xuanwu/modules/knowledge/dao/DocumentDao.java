package xuanwu.modules.knowledge.dao;

import org.apache.ibatis.annotations.Mapper;
import xuanwu.common.dao.BaseDao;
import xuanwu.modules.knowledge.entity.DocumentEntity;

/**
 * 文档 DAO
 */
@Mapper
public interface DocumentDao extends BaseDao<DocumentEntity> {
}
