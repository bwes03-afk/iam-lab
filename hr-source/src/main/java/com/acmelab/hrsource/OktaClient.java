package com.acmelab.hrsource;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import java.util.Map;

@Component
public class OktaClient {
    private final RestClient http;

    public OktaClient(@Value("${okta.org-url}") String orgUrl,
                      @Value("${okta.api-token}") String token) {
        this.http = RestClient.builder()
            .baseUrl(orgUrl + "/api/v1")
            .defaultHeader("Authorization", "SSWS " + token)
            .defaultHeader("Accept", "application/json")
            .build();
    }

    private Map<String, Object> profile(Worker w) {
        return Map.of(
            "firstName", w.firstName, "lastName", w.lastName,
            "email", w.email, "login", w.email,
            "employeeNumber", w.employeeId, "department", w.department,
            "title", w.title, "managerId", w.managerId == null ? "" : w.managerId,
            "workLocation", w.location, "employmentStatus", w.status);
    }

    // Joiner: create the user staged (not active) so nothing works before start date
    public void createStaged(Worker w) {
        http.post().uri("/users?activate=false")
            .body(Map.of("profile", profile(w)))
            .retrieve().toBodilessEntity();
    }

    // Mover and any HR change: POST is a partial update in Okta
    public void update(Worker w) {
        http.post().uri("/users/{login}", w.email)
            .body(Map.of("profile", profile(w)))
            .retrieve().toBodilessEntity();
    }
}