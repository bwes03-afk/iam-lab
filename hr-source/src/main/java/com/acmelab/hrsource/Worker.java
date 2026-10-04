package com.acmelab.hrsource;

import jakarta.persistence.*;
import java.time.LocalDate;

@Entity
public class Worker {
    @Id public String employeeId;
    public String firstName, lastName, email, department, title, location, managerId;
    public LocalDate startDate;
    public String status; // PENDING, ACTIVE, LEAVE, TERMINATED
}