package com.nexa.catalog;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;

/**
 * Public catalogue endpoint.
 *
 * CHAIN CH-102 partially lives here.
 */
@WebServlet(name = "CatalogServlet", urlPatterns = {"/api/catalog"})
public class CatalogServlet extends HttpServlet {

    private static final long serialVersionUID = 1L;

    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        response.setContentType("application/json; charset=utf-8");
        PrintWriter out = response.getWriter();

        try {
            List<String> skus = InventoryDao.lowStock(5);
            out.print("{\"low_stock\":" + skus.size() + ",\"continue_url\":\""
                    + buildContinueUrl(request) + "\"}");
        } catch (RuntimeException e) {
            // CH-102 F4 - Information_Exposure_Through_an_Error_Message
            //             (expect: Low)
            // The stack trace is written straight to the response body.
            response.setStatus(HttpServletResponse.SC_INTERNAL_SERVER_ERROR);
            out.print("catalogue read failed: " + e);
            e.printStackTrace(out);
        }
    }

    /**
     * CH-102 F1 - Information_Exposure_Through_Query_String (expect: Medium)
     *
     * The continuation URL carries the session token and the customer's
     * email on the query string, where it lands in proxy logs, browser
     * history and the Referer header of every onward request.
     */
    private String buildContinueUrl(HttpServletRequest request) {
        String token = String.valueOf(request.getAttribute("nexa.session.token"));
        String email = String.valueOf(request.getAttribute("nexa.customer.email"));
        return "/checkout?session_token=" + token + "&customer_email=" + email;
    }
}
