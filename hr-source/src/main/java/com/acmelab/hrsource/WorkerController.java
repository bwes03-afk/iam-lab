package com.acmelab.hrsource;

import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/workers")
public class WorkerController {
    private final WorkerRepository repo;
    private final OktaClient okta;

    public WorkerController(WorkerRepository repo, OktaClient okta) {
        this.repo = repo; this.okta = okta;
    }

    @GetMapping public List<Worker> all() { return repo.findAll(); }

    @PostMapping // hire
    public Worker hire(@RequestBody Worker w) {
        w.status = "PENDING";
        repo.save(w);
        okta.createStaged(w);
        return w;
    }

    @PostMapping("/{id}/transfer") // mover
    public Worker transfer(@PathVariable String id, @RequestParam String department,
                           @RequestParam(required = false) String managerId) {
        Worker w = repo.findById(id).orElseThrow();
        w.department = department;
        if (managerId != null) w.managerId = managerId;
        repo.save(w);
        okta.update(w);
        return w;
    }

    @PostMapping("/{id}/terminate") // leaver
    public Worker terminate(@PathVariable String id) {
        Worker w = repo.findById(id).orElseThrow();
        w.status = "TERMINATED";
        repo.save(w);
        okta.update(w); // Workflows reacts to employmentStatus
        return w;
    }
}