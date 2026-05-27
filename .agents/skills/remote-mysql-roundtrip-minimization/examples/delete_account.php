<?php

include_once 'config.php';

$account_id = filter_input(INPUT_POST, 'account_id');

$sql = "SELECT (SELECT COUNT(*) FROM accounts WHERE account_id='$account_id') AS account_exists, (SELECT COUNT(*) FROM accounts WHERE parent_account_id='$account_id') AS child_count, (SELECT COUNT(*) FROM transactionsv2 WHERE from_account_id='$account_id' OR to_account_id='$account_id') AS transaction_count;
DELETE a FROM accounts a WHERE a.account_id='$account_id' AND NOT EXISTS (SELECT 1 FROM (SELECT account_id FROM accounts WHERE parent_account_id='$account_id') c) AND NOT EXISTS (SELECT 1 FROM transactionsv2 WHERE from_account_id='$account_id' OR to_account_id='$account_id');";

if (!$con->multi_query($sql)) {
    echo json_encode(array('status' => "1", 'error' => $con->error));
    return;
}

$row = $con->store_result()->fetch_assoc();
$con->next_result();
$affected = $con->affected_rows;

if ($affected > 0) {
    echo json_encode(array('status' => "0"));
    return;
}

if ((int) $row['account_exists'] === 0) {
    echo json_encode(array('status' => "1", 'error' => "Account not found."));
    return;
}
echo json_encode(array('status' => "1", 'error' => "Account cannot be deleted : " . (int) $row['child_count'] . " child account(s), " . (int) $row['transaction_count'] . " transaction(s) reference this account."));
