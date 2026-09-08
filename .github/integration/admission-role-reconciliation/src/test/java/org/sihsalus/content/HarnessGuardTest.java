package org.sihsalus.content;

import static org.junit.Assert.*;

import java.nio.file.Path;
import java.util.Map;
import org.junit.Test;

/** These tests never connect to a database. */
public class HarnessGuardTest {
    @Test
    public void refusesImplicitOrArbitraryDatabaseTargets() {
        assertThrows(IllegalArgumentException.class, () -> AdmissionMigrationTest.validatePort(Map.of()));
        assertThrows(IllegalArgumentException.class, () -> AdmissionMigrationTest.validatePort(Map.of(
            "ADMISSION_TEST_DATABASE_DISPOSABLE", "openmrs", "ADMISSION_TEST_DB_PORT", "3306")));
        for (String invalid : new String[] {"", "0", "65536", "-1", "3306/openmrs", "host:3306", "3306?user=root"}) {
            assertThrows(IllegalArgumentException.class, () -> AdmissionMigrationTest.validatePort(Map.of(
                "ADMISSION_TEST_DATABASE_DISPOSABLE", AdmissionMigrationTest.DATABASE, "ADMISSION_TEST_DB_PORT", invalid)));
        }
    }

    @Test
    public void acceptsOnlyAnExplicitSyntheticDatabaseAndNumericPort() {
        assertEquals("12345", AdmissionMigrationTest.validatePort(Map.of(
            "ADMISSION_TEST_DATABASE_DISPOSABLE", AdmissionMigrationTest.DATABASE, "ADMISSION_TEST_DB_PORT", "12345")));
    }

    @Test
    public void readsActualCandidateCsvAsPolicyOracle() throws Exception {
        Path csv = Path.of(System.getProperty("content.root"))
            .resolve("configuration/backend_configuration/roles/roles-core.csv");
        var privileges = AdmissionMigrationTest.readAdmissionPrivileges(csv);
        assertTrue(privileges.contains("Delete Relationships"));
        assertFalse(privileges.contains("Purge Relationships"));
    }
}
