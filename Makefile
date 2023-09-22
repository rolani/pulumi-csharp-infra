setup:
	pip install -r requirements.txt

run:
	pulumi up -s production --yes

deploy: setup run

cleanup: 
	pulumi destroy -s production --yes

remove:
	pulumi stack rm production 

destroy: cleanup remove
