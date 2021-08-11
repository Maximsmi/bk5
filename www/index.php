<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <title>Управление telegramm-bot'ом</title>
 </head>
 
 <body>
  <table border="1" width="100%" height="100%" cellspacing="0" cellpadding="5" align="center">
	<!--Строка 1 - шапка сайта-->
	<tr>
		<td heght="120" colspan="3" bgcolor="#98FB98">
			<?php
			require('top.inc');
			?>
		</td>
	</tr>
	<!-- Строка 2- центральная часть сайта-->
	<tr> 
		<!-- Левая колонка с меню -->
		<td width="400" valign="top" bgcolor="#D3D3D3">
			<?php
			require('left-menu.inc');
			?>
		</td>
		<!-- Центральная часть сайта с инфой -->
		<td valign="top">
			Правая колонка
		</td>
	</tr>
	<!-- Подвал сайта -->
	<tr>
		<td heght="120" colspan="3" bgcolor="#708090">
			<?php
			require('buttom.inc');
			?>
		</td>
	
	</tr>
	
  </table>
 </body>
</html>

<table class="city_list">
	<?php foreach ($array as $items): ?>
	<tr>
		<?php foreach ($items as $row): ?>
		<td><?php echo $row; ?></td>
		<?php endforeach; ?>
	</tr>
	<?php endforeach; ?>
</table>
 
<style>
.city_list {
	width: 100%;
}
.city_list td {
	width: 25%;
	border: 1px solid #ddd;
	padding: 7px 10px;
}
.menu-row {
	float: left;
	box-sizing: border-box;
	width: calc(100% - 2px);
	padding: 7px 10px;
	background: #eee;
	margin: 1px; 
}
</style>

<?php
echo "Привет мир!!!"
?>

<?php

// Открываем базу данных
$db = new SQLite3('/home/pi/telegramm/db/database_id.db');
// отправляем запрос
$sql = "SELECT * FROM users";
$result = $db->query($sql);

$array = array();
while($data = $result->fetchArray(SQLITE3_ASSOC))
{
	$array[] = $data;
}

foreach($array as $row)
{
		print_r ($row);
		
}

// Закрываем базу данных
$db->close();

?>
*/
