package xuanwu.modules.agent.service;

import java.util.List;

import xuanwu.modules.agent.dto.AgentTagDTO;
import xuanwu.modules.agent.entity.AgentTagEntity;

public interface AgentTagService {

    AgentTagEntity saveTag(String tagName);

    void deleteTag(String tagId);

    List<AgentTagDTO> getTagsByAgentId(String agentId);

    void saveAgentTags(String agentId, List<String> tagIds, List<String> tagNames);

    void deleteAgentTags(String agentId);

    List<AgentTagDTO> getTagsByAgentIds(List<String> agentIds);

    List<AgentTagDTO> getAllTags();

    List<String> getAgentIdsByTagName(String tagName);
}
