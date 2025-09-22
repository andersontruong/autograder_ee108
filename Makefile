autograder_%: clean_%
	$(eval LAB_DIR=$(@:autograder_%=%)/)
	zip -j -r $@.zip runner.py setup.sh $(LAB_DIR) 

clean_%:
	$(eval LAB_DIR=$(@:clean_%=%)/)
	@cd $(LAB_DIR)
	rm -rf __pycache__/ sim_build/ *.json
