deploy:
	pulumi up -s production --yes

destroy: 
	pulumi destroy -s production --yes