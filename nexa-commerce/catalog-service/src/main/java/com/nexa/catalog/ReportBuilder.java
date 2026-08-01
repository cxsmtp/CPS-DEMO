package com.nexa.catalog;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

/**
 * Nightly stock report writer.
 *
 * CHAIN CH-103 partially lives here. The report location comes from a
 * stored configuration file rather than from a request, which is why the
 * traversal below is the Medium "stored relative" variant and not the
 * High direct-traversal variant.
 */
public final class ReportBuilder {

    private static final Properties SETTINGS = new Properties();

    static {
        try (InputStream in = ReportBuilder.class
                .getResourceAsStream("/catalog-settings.properties")) {
            if (in != null) {
                SETTINGS.load(in);
            }
        } catch (IOException e) {
            System.out.println("[catalog] settings load failed");
        }
    }

    private ReportBuilder() {
    }

    /**
     * CH-103 F3 - Stored_Relative_Path_Traversal (expect: Medium)
     *
     * The relative report directory is read from stored settings and joined
     * without canonicalisation, so a stored value containing ../ escapes the
     * intended directory. The source is the settings file, not the request.
     */
    public static File reportTarget(String reportName) {
        String storedDir = SETTINGS.getProperty("report.dir", "reports");
        return new File(storedDir + File.separator + reportName + ".csv");
    }

    /**
     * CH-103 F4 - Creation_of_Temp_File_in_Dir_with_Incorrect_Permissions
     *             (expect: Low)
     * CH-103 F5 - Race_Condition (expect: Low)
     *
     * The staging file is created in the shared system temp directory with
     * default permissions, and the exists()/delete()/write sequence leaves a
     * window in which another process can substitute the path between the
     * check and the write.
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
