deploy:
	pulumi up -s production --yes

cleanup: 
	pulumi destroy -s production --yes

remove:
	pulumi stack rm production 

destroy: cleanup remove
