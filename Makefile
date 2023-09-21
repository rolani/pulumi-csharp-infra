setup:
	git clone https://github.com/rolani/infra-team-test.git  &&\
		cd infra-team-test
deploy:
	pulumi up -s production --yes

destroy: 
	pulumi destroy -s production --yes
