package xuanwu.modules.agent.dao;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import xuanwu.common.dao.BaseDao;
import xuanwu.modules.agent.entity.AgentTagRelationEntity;

import java.util.List;

@Mapper
public interface AgentTagRelationDao extends BaseDao<AgentTagRelationEntity> {

    int deleteByAgentId(@Param("agentId") String agentId);

    int insertRelation(AgentTagRelationEntity relation);

    int batchInsertRelation(@Param("list") List<AgentTagRelationEntity> relations);
}
