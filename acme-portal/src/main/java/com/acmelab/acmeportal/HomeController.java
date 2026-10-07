package com.acmelab.acmeportal;

import java.util.Map;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.core.oidc.user.OidcUser;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HomeController {

    // Shows the claims Okta put in the ID token
    @GetMapping("/")
    public Map<String, Object> home(@AuthenticationPrincipal OidcUser user) {
        return user.getClaims();
    }

    // Raw ID token, for inspecting at jwt.io (lab only, never real tokens)
    @GetMapping("/token")
    public String token(@AuthenticationPrincipal OidcUser user) {
        return user.getIdToken().getTokenValue();
    }
}