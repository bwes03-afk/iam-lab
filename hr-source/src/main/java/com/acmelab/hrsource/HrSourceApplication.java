package com.acmelab.hrsource;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class HrSourceApplication {

    public static void main(String[] args) {
        SpringApplication.run(HrSourceApplication.class, args);
    }
}