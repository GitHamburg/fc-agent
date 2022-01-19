package main

import (
	"io/fs"
	"io/ioutil"
)

func main() {

	codegen := codeGen{}
	v1Config := codegen.createV1Config()
	err := ioutil.WriteFile("./pkg/integrations/v1/config.go", []byte(v1Config), fs.ModePerm)
	if err != nil {
		panic(err)
	}

	v2Config := codegen.createV2Config()
	err = ioutil.WriteFile("./pkg/integrations/v2/config.go", []byte(v2Config), fs.ModePerm)
	if err != nil {
		panic(err)
	}

}