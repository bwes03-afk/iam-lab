package com.acmelab.scimservice;

import jakarta.servlet.*;
import jakarta.servlet.http.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import java.io.IOException;

@Component
public class TokenFilter implements Filter {
    @Value("${scim.token}") private String token;

    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {
        var auth = ((HttpServletRequest) req).getHeader("Authorization");
        if (!("Bearer " + token).equals(auth)) {
            ((HttpServletResponse) res).sendError(401);
            return;
        }
        chain.doFilter(req, res);
    }
}