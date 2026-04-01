package xuanwu.modules.security.service.impl;

import org.springframework.stereotype.Service;

import lombok.AllArgsConstructor;
import xuanwu.modules.security.dao.SysUserTokenDao;
import xuanwu.modules.security.entity.SysUserTokenEntity;
import xuanwu.modules.security.service.ShiroService;
import xuanwu.modules.sys.dao.SysUserDao;
import xuanwu.modules.sys.entity.SysUserEntity;

@AllArgsConstructor
@Service
public class ShiroServiceImpl implements ShiroService {
    private final SysUserDao sysUserDao;
    private final SysUserTokenDao sysUserTokenDao;

    @Override
    public SysUserTokenEntity getByToken(String token) {
        return sysUserTokenDao.getByToken(token);
    }

    @Override
    public SysUserEntity getUser(Long userId) {
        return sysUserDao.selectById(userId);
    }
}