<?php
$servername = "localhost";
$db_username = "root";
$db_password = "root";

$conn = new mysqli($servername, $db_username, $db_password, "db");
if ($conn->connect_error) {
	die("Connection failed: " . $conn->connect_error);
} 

$rfid = $_GET["rfid"];
$nama = $_GET["id"];
$sql = "INSERT INTO rfid_x (idkegiatan, rfid) VALUES ('$idkegiatan', '$rfid')";

if(mysqli_query($conn, $sql)){
	echo "Success!";
} else {
}
?>
