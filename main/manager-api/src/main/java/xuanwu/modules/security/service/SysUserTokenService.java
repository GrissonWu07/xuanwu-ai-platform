package xuanwu.modules.security.service;

import xuanwu.common.page.TokenDTO;
import xuanwu.common.service.BaseService;
import xuanwu.common.utils.Result;
import xuanwu.modules.security.entity.SysUserTokenEntity;
import xuanwu.modules.sys.dto.PasswordDTO;
import xuanwu.modules.sys.dto.SysUserDTO;

/**
 * 用户Token
 * Copyright (c) 人人开源 All rights reserved.
 * Website: https://www.renren.io
 */
public interface SysUserTokenService extends BaseService<SysUserTokenEntity> {

    /**
     * 生成token
     *
     * @param userId 用户ID
     */
    Result<TokenDTO> createToken(Long userId);

    SysUserDTO getUserByToken(String token);

    /**
     * 退出
     *
     * @param userId 用户ID
     */
    void logout(Long userId);

    /**
     * 修改密码
     *
     * @param userId
     * @param passwordDTO
     */
    void changePassword(Long userId, PasswordDTO passwordDTO);

}