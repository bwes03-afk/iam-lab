package com.acmelab.hrsource;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
public class SecurityConfig {

    @Bean
    SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            // Stateless API with bearer tokens, so no browser CSRF protection needed
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth
                // Reporting API: requires a token carrying the hr.read scope
                .requestMatchers("/api/**").hasAuthority("SCOPE_hr.read")
                // Lab admin endpoints stay open (a production system would protect these too)
                .anyRequest().permitAll())
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()));
        return http.build();
    }
}