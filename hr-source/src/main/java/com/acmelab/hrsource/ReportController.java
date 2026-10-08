package com.acmelab.hrsource;

import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ReportController {
    private final WorkerRepository repo;

    public ReportController(WorkerRepository repo) { this.repo = repo; }

    // Protected by SecurityConfig: needs a valid token with hr.read
    @GetMapping("/api/workers")
    public List<Worker> workers() { return repo.findAll(); }
}