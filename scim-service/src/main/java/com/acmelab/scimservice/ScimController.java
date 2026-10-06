package com.acmelab.scimservice;

import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@RestController
@RequestMapping("/scim/v2")
public class ScimController {
    private static final String USER_SCHEMA = "urn:ietf:params:scim:schemas:core:2.0:User";
    private static final String LIST_SCHEMA = "urn:ietf:params:scim:api:messages:2.0:ListResponse";
    private final Map<String, Map<String, Object>> users = new ConcurrentHashMap<>();

    @GetMapping("/Users")
    public Map<String, Object> list(@RequestParam(required = false) String filter) {
        List<Map<String, Object>> found = new ArrayList<>(users.values());
        if (filter != null && filter.startsWith("userName eq ")) {
            String wanted = filter.substring(12).replace("\"", "");
            found.removeIf(u -> !wanted.equalsIgnoreCase((String) u.get("userName")));
        }
        return Map.of("schemas", List.of(LIST_SCHEMA), "totalResults", found.size(),
                      "startIndex", 1, "itemsPerPage", found.size(), "Resources", found);
    }

    @PostMapping("/Users")
    public ResponseEntity<Map<String, Object>> create(@RequestBody Map<String, Object> body) {
        String userName = (String) body.get("userName");
        boolean exists = users.values().stream()
            .anyMatch(u -> userName.equalsIgnoreCase((String) u.get("userName")));
        if (exists) return ResponseEntity.status(409).body(error(409, "User already exists"));
        String id = UUID.randomUUID().toString();
        body.put("id", id);
        body.put("schemas", List.of(USER_SCHEMA));
        users.put(id, body);
        return ResponseEntity.status(201).body(body);
    }

    @GetMapping("/Users/{id}")
    public ResponseEntity<Map<String, Object>> get(@PathVariable String id) {
        var u = users.get(id);
        return u == null ? ResponseEntity.status(404).body(error(404, "Not found")) : ResponseEntity.ok(u);
    }

    @PutMapping("/Users/{id}")
    public ResponseEntity<Map<String, Object>> replace(@PathVariable String id, @RequestBody Map<String, Object> body) {
        if (!users.containsKey(id)) return ResponseEntity.status(404).body(error(404, "Not found"));
        body.put("id", id);
        users.put(id, body);
        return ResponseEntity.ok(body);
    }

    @PatchMapping("/Users/{id}")
    @SuppressWarnings("unchecked")
    public ResponseEntity<Map<String, Object>> patch(@PathVariable String id, @RequestBody Map<String, Object> body) {
        var u = users.get(id);
        if (u == null) return ResponseEntity.status(404).body(error(404, "Not found"));
        for (var op : (List<Map<String, Object>>) body.get("Operations")) {
            if (op.get("value") instanceof Map<?, ?> v) u.putAll((Map<String, Object>) v);
        }
        return ResponseEntity.ok(u);
    }

    private Map<String, Object> error(int status, String detail) {
        return Map.of("schemas", List.of("urn:ietf:params:scim:api:messages:2.0:Error"),
                      "status", String.valueOf(status), "detail", detail);
    }
}