package com.acmelab.hrsource;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import java.time.LocalDate;

@Component
public class StartDateJob {
    private final WorkerRepository repo;
    private final OktaClient okta;

    public StartDateJob(WorkerRepository repo, OktaClient okta) {
        this.repo = repo; this.okta = okta;
    }

    // Every 5 minutes for the lab. A real HR feed would run daily.
    @Scheduled(fixedRate = 300_000)
    public void activateStarters() throws InterruptedException {
        LocalDate today = LocalDate.now();
        for (Worker w : repo.findAll()) {
            boolean started = w.startDate != null && !w.startDate.isAfter(today);
            if ("PENDING".equals(w.status) && started) {
                w.status = "ACTIVE";
                repo.save(w);
                okta.update(w);       // sets employmentStatus=ACTIVE in Okta
                Thread.sleep(300);    // stay under Okta rate limits
            }
        }
    }
}