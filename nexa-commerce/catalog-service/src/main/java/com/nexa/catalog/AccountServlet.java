package com.nexa.catalog;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import java.io.IOException;
import java.io.PrintWriter;
import java.util.logging.Logger;

/**
 * Customer account endpoint.
 *
 * CHAIN CH-102 completes here.
 *
 * FIX (scan cc434dd7): the previous revision read values with
 * request.getAttribute(). That is not a taint source, so Privacy_Violation,
 * Heap_Inspection and the sensitive-exposure finding never fired. Values now
 * come from request.getParameter(), matching JavaVulnerableLab's shape. None
 * of them reaches a query, a command or a file path, so no High-rated sink
 * is created.
 */
@WebServlet(name = "AccountServlet", urlPatterns = {"/api/account"})
public class AccountServlet extends HttpServlet {

    private static final long serialVersionUID = 1L;
    private static final Logger LOG = Logger.getLogger(AccountServlet.class.getName());

    /**
     * CH-102 F5 - Heap_Inspection (expect: Low)
     *
     * The credential is held in a String. Strings are immutable and cannot be
     * zeroed, so the value stays resident in the heap until GC decides
     * otherwise and lands in any crash dump taken in between. A char[] that
     * can be wiped is the correct type here.
     */
    private String password;

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        String customerRef = request.getParameter("customer_ref");
        String email = request.getParameter("email");
        this.password = request.getParameter("passphrase");

        // CH-102 F3 - Privacy_Violation (expect: Medium)
        // Customer email and passphrase are written to the application log.
        LOG.info("account update ref=" + customerRef
                + " email=" + email
                + " password=" + this.password);

        response.setContentType("application/json; charset=utf-8");
        PrintWriter out = response.getWriter();

        // CH-102 F2 - Exposure of Sensitive Information to an Unauthorized
        //             Actor (expect: Medium)
        //
        // The response body returns the stored billing identifiers and the
        // internal customer key to whoever asked; there is no authorisation
        // check between the request and this data.
        out.print("{\"customer_ref\":\"" + customerRef + "\","
                + "\"email\":\"" + email + "\","
                + "\"internal_key\":\"IK-" + Integer.toHexString(
                        String.valueOf(customerRef).hashCode()) + "\","
                + "\"stored_card_last4\":\"4242\","
                + "\"billing_account\":\"NX-BILL-88213\","
                + "\"password_on_file\":\"" + this.password + "\"}");
    }
}
