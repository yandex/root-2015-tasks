local function get_cookie(filename)
    return ngx.encode_base64(ngx.sha1_bin(ngx.today() .. ngx.var.auth_cookie_salt .. filename .. ngx.var.auth_cookie_salt))
end

local filename = ngx.var.auth_cookie_filename
local set_cookie = ngx.var.auth_cookie_set

if set_cookie == '1' then
    cookie = get_cookie(filename)
    ngx.header['Set-Cookie'] = string.format('%s=%s; path=/; expires=%s',
        'auth_' .. filename,
        cookie,
        ngx.cookie_time(ngx.time() + 24 * 3600)
    )
    ngx.status = 200
    ngx.exit(200)
else
    cookie = get_cookie(filename)
    user_cookie = ngx.var['cookie_auth_' .. filename]

    if not user_cookie then
        ngx.status = 403
        ngx.exit(403)
    end
    if user_cookie ~= cookie then
        ngx.status = 403
        ngx.exit(403)
    end
end


