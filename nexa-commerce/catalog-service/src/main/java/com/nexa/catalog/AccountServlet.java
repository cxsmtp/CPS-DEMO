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
 */
@WebServlet(name = "AccountServlet", urlPatterns = {"/api/account"})
public class AccountServlet extends HttpServlet {

    private static final long serialVersionUID = 1L;
    private static final Logger LOG = Logger.getLogger(AccountServlet.class.getName());

    /**
     * CH-102 F5 - Heap_Inspection (expect: Low)
     *
     * The credential is held in a String. Strings are immutable and cannot
     * be zeroed, so the value stays resident in the heap until GC decides
     * otherwise and lands in any crash dump taken in between. A char[] that
     * can be wiped is the correct type here.
     */
    private String lastPassphrase;

    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        String customerRef = String.valueOf(request.getAttribute("nexa.customer.ref"));
        String email = String.valueOf(request.getAttribute("nexa.customer.email"));
        this.lastPassphrase = String.valueOf(request.getAttribute("nexa.customer.pass"));

        // CH-102 F3 - Privacy_Violation (expect: Medium)
        // Customer email and passphrase are written to the application log.
        LOG.info("account update ref=" + customerRef
                + " email=" + email
                + " passphrase=" + this.lastPassphrase);

        response.setContentType("application/json; charset=utf-8");
        PrintWriter out = response.getWriter();
        out.print(billingSummary(customerRef, email));
    }

    /**
     * CH-102 F2 - Exposure of Sensitive Information to an Unauthorized Actor
     *             (expect: Medium)
     *
     * The response body includes the stored billing identifiers and the
     * internal customer key regardless of who is asking; there is no
     * authorisation check between the request and this data.
     */
    private String billingSummary(String customerRef, String email) {
        return "{\"customer_ref\":\"" + customerRef + "\","
                + "\"email\":\"" + email + "\","
                + "\"internal_key\":\"" + internalKeyFor(customerRef) + "\","
                + "\"stored_card_last4\":\"4242\","
                + "\"billing_account\":\"NX-BILL-88213\"}";
    }

    private String internalKeyFor(String customerRef) {
        return "IK-" + Integer.toHexString(customerRef.hashCode());
    }
}
