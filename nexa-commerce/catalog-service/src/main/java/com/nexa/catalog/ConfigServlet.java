package com.nexa.catalog;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;
import java.io.PrintWriter;

/**
 * Operations endpoint used by the merchandising team to retune the catalogue
 * at runtime.
 *
 * CHAIN CH-103 begins here.
 */
@WebServlet(name = "ConfigServlet", urlPatterns = {"/api/ops/config"})
public class ConfigServlet extends HttpServlet {

    private static final long serialVersionUID = 1L;

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        response.setContentType("application/json; charset=utf-8");
        PrintWriter out = response.getWriter();

        // CH-103 F2 - Parameter_Tampering (expect: Medium)
        //
        // The privilege and the price adjustment applied to this call are
        // taken from the request itself rather than from the authenticated
        // session, so the caller decides their own authorisation level.
        String role = request.getParameter("role");
        String discountPercent = request.getParameter("discount_percent");

        boolean privileged = "merchandiser".equals(role) || "ops".equals(role);
        if (!privileged) {
            response.setStatus(HttpServletResponse.SC_FORBIDDEN);
            out.print("{\"error\":\"insufficient role\"}");
            return;
        }

        // CH-103 F1 - External_Control_of_System_or_Config_Setting
        //             (expect: Medium)
        // A JVM-wide system property is set from a request parameter.
        String pageSize = request.getParameter("page_size");
        if (pageSize != null) {
            System.setProperty("nexa.catalog.pageSize", pageSize);
        }
        if (discountPercent != null) {
            System.setProperty("nexa.catalog.discount", discountPercent);
        }

        if ("1".equals(request.getParameter("rebuild_report"))) {
            ReportBuilder.writeReport("low-stock", "sku,on_hand\n");
        }

        out.print("{\"page_size\":\""
                + System.getProperty("nexa.catalog.pageSize", "20")
                + "\",\"role\":\"" + role + "\"}");
    }
}
