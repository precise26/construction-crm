<?php
// Enable error reporting for debugging
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Configuration for CRM API access
$crmConfig = [
    'api_url' => 'http://localhost:8000/api/website-form',
    'timeout' => 10 // seconds
];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Read the raw request body
    $data = file_get_contents('php://input');
    
    // Decode the JSON data
    $formData = json_decode($data, true);

    // Validate input data
    if (!$formData || !isset($formData['name']) || !isset($formData['email'])) {
        http_response_code(400);
        header('Content-Type: application/json');
        echo json_encode([
            'error' => 'Invalid form data',
            'received_data' => $formData
        ]);
        exit;
    }

    // Retrieve form data with fallback for optional fields
    $name = $formData['name'];
    $address = $formData['address'] ?? '';
    $phone = $formData['phone'] ?? '';
    $email = $formData['email'];
    $message = $formData['message'] ?? '';

    // Email body
    $email_body = "
        <p>Name: " . htmlspecialchars($name) . "</p>
        <p>Address: " . htmlspecialchars($address) . "</p>
        <p>Phone: " . htmlspecialchars($phone) . "</p>
        <p>Email: " . htmlspecialchars($email) . "</p>
        <p>Message: " . htmlspecialchars($message) . "</p>
    ";

    // Email parameters
    $to = 'admin@grandterradevelopments.ca';
    $subject = 'New Contact Form Submission';
    $headers = "From: " . htmlspecialchars($email) . "\r\n";
    $headers .= "Reply-To: " . htmlspecialchars($email) . "\r\n";
    $headers .= "Content-Type: text/html\r\n";

    // Prepare data for CRM API
    $crmData = [
        'name' => $name,
        'email' => $email,
        'phone' => $phone,
        'message' => $message,
        'project_type' => null,
        'address' => $address,
        'source' => 'Website Contact Form'
    ];

    // Initialize cURL
    $ch = curl_init($crmConfig['api_url']);
    
    // Set cURL options for secure API call
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($crmData));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json',
        'Accept: application/json'
    ]);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, $crmConfig['timeout']);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false); // Disable SSL verification for local development
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);

    // Execute cURL and get response
    $crmResponse = curl_exec($ch);
    $crmHttpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $crmError = curl_error($ch);
    curl_close($ch);

    // Send email
    $emailSent = mail($to, $subject, $email_body, $headers);

    // Prepare final response
    $response = [
        'email_sent' => $emailSent,
        'crm_status' => $crmHttpCode == 200 ? 'Lead created' : 'Failed to create lead',
        'crm_response' => json_decode($crmResponse, true),
        'crm_http_code' => $crmHttpCode
    ];

    if ($emailSent && $crmHttpCode == 200) {
        // Successful submission
        header('Content-Type: application/json');
        echo json_encode([
            'status' => 'success',
            'message' => 'Thank you for your interest in Grand Terra Developments. Your message was sent successfully and we will be in contact with you shortly.',
            'details' => $response
        ]);
    } else {
        // Partial or complete failure
        http_response_code(500);
        header('Content-Type: application/json');
        echo json_encode([
            'status' => 'error',
            'message' => 'There was an issue processing your submission. Please try again later.',
            'details' => $response
        ]);
    }
} else {
    // Method not allowed
    http_response_code(405);
    header('Content-Type: application/json');
    echo json_encode(['error' => 'Method Not Allowed']);
}
?>