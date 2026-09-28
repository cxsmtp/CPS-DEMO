package com.nexa.catalog;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

/**
 * Nightly stock report writer.
 *
 * CHAIN CH-103 completes here.
 *
 * FIX (scan cc434dd7): the report directory previously came from a
 * .properties file and nothing fired. It now comes from a database column,
 * which is the stored source JavaVulnerableLab uses for its Medium-rated
 * Stored_Relative_Path_Traversal. The source is still the datastore and never
 * the request, so this stays the stored variant rather than the High-rated
 * direct-traversal variant.
 */
public final class ReportBuilder {

    private static final String JDBC_URL = "jdbc:sqlite:catalog.sqlite";

    private ReportBuilder() {
    }

    /**
     * Read the configured report directory out of the settings table.
     */
    private static String storedReportDir() {
        String dir = "reports";
        String sql = "SELECT value FROM settings WHERE name = 'report.dir'";
        try (Connection cx = DriverManager.getConnection(JDBC_URL);
             Statement st = cx.createStatement();
             ResultSet rs = st.executeQuery(sql)) {
            if (rs.next()) {
                dir = rs.getString("value");
            }
        } catch (SQLException e) {
            System.out.println("[catalog] settings read failed");
        }
        return dir;
    }

    /**
     * CH-103 F3 - Stored_Relative_Path_Traversal (expect: Medium)
     *
     * The relative report directory is read from the settings table and
     * joined without canonicalisation, so a stored value containing ../
     * escapes the intended directory.
     */
    public static File reportTarget(String reportName) {
        String storedDir = storedReportDir();
        return new File(storedDir + File.separator + reportName + ".csv");
    }

    /**
     * CH-103 F4 - Creation_of_Temp_File_With_Insecure_Permissions
     *             (expect: Low)
     * CH-103 F5 - Race_Condition (expect: Low)
     *
     * The staging file is created in the shared system temp directory with
     * default permissions, and the exists() / delete() / write sequence
     * leaves a window in which another process can substitute the path
     * between the check and the write.
     */
    public static void writeReport(String reportName, String csvBody) {
        try {
            File staging = File.createTempFile("nexa-report-", ".tmp");

            if (staging.exists()) {
                staging.delete();
            }
            try (FileWriter writer = new FileWriter(staging)) {
                writer.write(csvBody);
            }

            File target = reportTarget(reportName);
            File parent = target.getParentFile();
            if (parent != null && !parent.exists()) {
                parent.mkdirs();
            }
            staging.renameTo(target);
        } catch (IOException e) {
            System.out.println("[catalog] report write failed");
        }
    }
}
