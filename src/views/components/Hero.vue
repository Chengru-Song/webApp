<template>
    <section class="section-hero section-shaped my-0">
        <div class="shape shape-style-1 shape-primary">
            <span class="span-150"></span>
            <span class="span-50"></span>
            <span class="span-50"></span>
            <span class="span-75"></span>
            <span class="span-100"></span>
            <span class="span-75"></span>
            <span class="span-50"></span>
            <span class="span-100"></span>
            <span class="span-50"></span>
            <span class="span-100"></span>
        </div>
        <div class="container shape-container d-flex align-items-center">
            <div class="col px-0">
                <div class="row justify-content-center align-items-center">
                    <div class="col-lg-7 text-center pt-lg">
                        <h1 class="text-white">Image classification</h1>
                        <p class="lead text-white mt-4 mb-5">A lightweight image classification platform. </p>
                        <el-upload
                            :on-change="change"
                            :on-preview="handlePreview"
                            :on-remove="handleRemove"
                            ref="uploadForm"
                            class="upload-demo"
                            action="#"
                            drag
                            :auto-upload="false"
                            accept=".jpeg,.jpg,.png"
                            :file-list="fileList"
                            multiple>
                            <i class="el-icon-upload"></i>
                            <div class="el-upload__text">Drag image file here, or <em>Click</em> to upload</div>
                            <div class="el-upload__tip text-white" slot="tip">Only jpg/png files are accepted，and the file should be less than 10MB</div>
                        </el-upload>
                        <div class="btn-wrapper">
                            <base-button tag="a"
                                         @click="submitUpload"
                                         class="mb-3 mb-sm-0"
                                         type="white"
                                         icon="ni ni-cloud-upload-96">
                                Upload
                            </base-button>
                        </div>
                        
                    </div>
                </div>
                <el-table
                    class="predict-table"
                    v-for="(table, key) in tableData"
                    :key="key"
                    :data="table"
                    :span-method="objectSpanMethod"
                    style="width: 100%">
                    <el-table-column
                        prop="filename"
                        label="Filename"
                        width="180">
                    </el-table-column>
                    <el-table-column
                        prop="class"
                        label="Class"
                        width="360">
                    </el-table-column>
                    <el-table-column
                        prop="confidence"
                        label="Confidence">
                    </el-table-column>
                </el-table>
                <div class="row align-items-center justify-content-around stars-and-coded">
                    <div class="col-md-12 text-center">
                        <span class="text-white alpha-7 ml-3">Star me on</span>
                        <a href="https://github.com/GetALittleRough/webApp" target="_blank" title="Support us on Github">
                            <img src="img/brand/github-white-slim.png" style="height: 22px; margin-top: -3px">
                        </a>
                    </div>
                </div>
            </div>

            <el-dialog
                title="View picture"
                :visible.sync="dialogVisible"
                width="50%"
                >
                <span><img :src="imageUrl" alt="" class="box-image"></span>
                <span slot="footer" class="dialog-footer">
                <base-button type="secondary" @click="dialogVisible = false">OK</base-button>
                <!-- <base-button type="primary" @click="dialogVisible = false">确 定</base-button> -->
                </span>
            </el-dialog>
        </div>
    </section>
</template>
<script>
import axios from 'axios'
export default {
    data() {
        return {
            dialogVisible: false,
            imageUrl: '',
            fileList: [],
            acceptFiles: ['image/jpeg', 'image/jpg', 'image/png'],
            // tableData: [{
            //     "filename": "t.jpg",
            //     "class":"Labrador retriever",
            //     "confidence":60.26504135131836 
            // }, {
            //     "filename": "t.jpg",
            //     "class":"Labrador retriever",
            //     "confidence":60.26504135131836
            // }, {
            //     "filename": "t.jpg",
            //     "class":"Labrador retriever",
            //     "confidence":60.26504135131836
            // }, {
            //     "filename": "t.jpg",
            //     "class":"Labrador retriever",
            //     "confidence":60.26504135131836
            // }, {
            //     "filename": "t.jpg",
            //     "class":"Labrador retriever",
            //     "confidence":60.26504135131836
            // }]
            tableData: []
        };
    },
    methods: {
        change(file, fileList) {
            if(this.beforeUpload(file)) {
                this.fileList.push(file)
            }
        },
        handleRemove(file, fileList) {
            this.fileList = fileList
            this.tableData.pop()
        },
        beforeUpload(file) {
            const isLt10M = file.size / 1024 / 1024 < 5
            if(!isLt10M) {
                this.$message.error('Image size must be less than 10MB')
            }
            return isLt10M
        },
        submitUpload() {
            let formData = new FormData()
            const headerConfig = {headers: {'Content-Type': 'multipart/form-data'}}
            let flag = true
            this.fileList.forEach(file => {
                if(this.acceptFiles.indexOf(file.raw.type) == -1) {
                    flag = false
                } else {
                    formData.append('files', file.raw)
                }
            })
            if(!flag) {
                this.$message.error('Only accept jpg and png images!')
            }
            const images = formData.get('files')
            if(images == null) {
                this.$message.error('No file specified')
            } else {
                axios.post(this.global.baseUrl+"/images/", formData, headerConfig).then(res => {
                    this.tableData = []
                    const tableData = res.data.predictions
                    for(let i=0; i<tableData.length; i++) {
                        const tempData = []
                        tableData[i].forEach(predict => {
                            tempData.push({
                                "filename": this.fileList[i].name,
                                "class": predict[0],
                                "confidence": predict[1]
                            })
                        })
                        this.tableData.push(tempData)
                    }

                }).catch(err => {
                    console.error(err)

                })
            }
        },
        handlePreview(file) {
            const reader = new FileReader();
            reader.readAsDataURL(file.raw)
            reader.onloadend = (ev) => {
                this.imageUrl = ev.target.result
                this.dialogVisible = true
            }
        }, 
        objectSpanMethod({ row, column, rowIndex, columnIndex }) {
            if (columnIndex == 0 && rowIndex == 0) {
                return {
                    rowspan: 5,
                    colspan: 1
                }
            } else if(columnIndex == 0 && rowIndex != 0) {
                return {
                    rowspan: 0,
                    colspan: 0
                }
            }
        }

    }
};
</script>
<style lang="scss" scoped>
.btn-wrapper {
    margin: 2vh auto;
}
.box-image {
  width: 100%;
}
.modal-dialog {
  max-width: 50%;
}
.el-upload-list {
    background-color: #fff;
}
.predict-table {
    margin-top: 2vh;
}
</style>
