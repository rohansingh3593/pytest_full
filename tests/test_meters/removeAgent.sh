#!/bin/bash

DBRETRIES=20 
SUCCESS=0
DATABASE_ERROR=1
dbpath="/usr/share/itron/database/muse01.db"

execute_db_query() {
	local retrycount=0
	local dbstatus=0
	local output=""
	dboperation=${1}

	while [ $dbstatus -eq $SUCCESS ] && [ $retrycount -ne $DBRETRIES ]; do

		let "retrycount++"

		# sqlite3 returns status code of '0' even when there is a syntax problem in the database command
		# it is not advisable to check status code rather it is always good to check error output
		output=$( echo $echo_args "$dboperation" | sqlite3 -bail -batch $dbpath 2>&1 )
		echo "$output" | grep -q 'Error:'
		dbstatus=$?
	done

	if [ $dbstatus -eq $SUCCESS ]; then
		echo "database operation unsuccessful! reason=$output"
		return $DATABASE_ERROR
	fi
	#Don't interpret the \ in the output regardless of if we interpreted the input
	echo -E "$output"

	return $SUCCESS

}

if [ -z $1 ]
then
	echo "No agent id given"
	exit
fi

agentid=$1

overlayid=$(execute_db_query "select overlayuid from agentinformation where agentuid=$agentid;" || return $?)

if [ "$overlayid" = "" ] || [ "overlayid" = "$DATABASE_ERROR" ]
then
	echo "Agent not present"
	exit
fi

overlaypath=$(execute_db_query "select overlaypath from overlaysetup where uid=$overlayid;" || return $?)
containerid=$(execute_db_query "select containeruid from containeroverlay where overlayuid=$overlayid;" || return $?)
agentidhex=`printf "%08x" $agentid`

pscount=`ps | grep $agentidhex | grep -v grep | grep _Daemon | wc -l`
if [ $pscount -ne 1 ]
then
	echo "Agent not running"
	#exit # Uninstall non running agents as well
fi

echo "AgentId: $agentid"
echo "OverlayId: $overlayid"

if [ "$containerid" = "$DATABASE_ERROR" ]; then
	echo "ContainerId: Not Found"
else
	echo "ContainerId: $containerid"
fi

if [ "$overlaypath" = "$DATABASE_ERROR" ]; then
	echo "OverlayPath: Not Found"
else
	echo "OverlayPath: $overlaypath"
fi

deletestatus=$(execute_db_query "delete from containeroverlay where overlayuid=$overlayid;" || return $?)
if [ "$deletestatus" = "$DATABASE_ERROR" ]; then echo "delete from containeroverlay failed"; fi

deletestatus=$(execute_db_query "delete from agentregistration where id=$agentid;" || return $?)
if [ "$deletestatus" = "$DATABASE_ERROR" ]; then echo "delete from agentregistration failed"; fi

deletestatus=$(execute_db_query "delete from agentpolicy where agentid=$agentid;" || return $?)
if [ "$deletestatus" = "$DATABASE_ERROR" ]; then echo "delete from agentpolicy failed"; fi

deletestatus=$(execute_db_query "delete from agentmailbox where agentid=$agentid;" || return $?)
if [ "$deletestatus" = "$DATABASE_ERROR" ]; then echo "delete from agentmailbox failed"; fi

deletestatus=$(execute_db_query "delete from agentinformation where agentuid=$agentid;" || return $?)
if [ "$deletestatus" = "$DATABASE_ERROR" ]; then echo "delete from agentinformation failed"; fi

deletestatus=$(execute_db_query "delete from overlayconfiguration where uid=$overlayid;" || return $?)
if [ "$deletestatus" = "$DATABASE_ERROR" ]; then echo "delete from overlayconfiguration failed"; fi

deletestatus=$(execute_db_query "delete from overlaysetup where uid=$overlayid;" || return $?)
if [ "$deletestatus" = "$DATABASE_ERROR" ]; then echo "delete from overlaysetup failed"; fi

rm $overlaypath
for f in `grep "^feature=" /tmp/container/$containerid/rootfs/etc/agents.d/$agentidhex.info | cut -d= -f2`
do
  fid=$(($f))
  status=$(execute_db_query "delete from featureconfiguration where featureid=$fid;" || return $?)
  if [ "$status" = "$DATABASE_ERROR" ]; then echo "delete $fid in featureconfiguration failed"; fi
done

echo " Complete : Refreshing Containers"
dbus-send --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.StopAllContainer
dbus-send --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.Refresh

