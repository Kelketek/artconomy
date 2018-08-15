<template>
  <v-card class="mt-3 elevation-5">
    <v-card-text>
    <v-card-title><strong><label :for="schema.id">{{schema.label}}</label></strong></v-card-title>
      <div class="upload text-xs-center" :class="{'error--text': errors.length}">
        <div v-if="value.length">
          <v-btn v-if="value.length" color="normal" @click="value = []">Reset</v-btn>
          <div>
            <img :src="getUrl(value[0])" style="max-width: 15rem;max-height: 15rem">
            <div>
              <span>{{value[0].name}}</span> -
              <span>{{value[0].size | formatSize}}</span>
              <span v-if="value[0].error">{{value[0].error}}</span>
              <span v-else-if="value[0].success">success</span>
              <span v-else-if="value[0].active">active</span>
              <span v-else-if="value[0].active">active</span>
            </div>
          </div>
        </div>
        <div v-else class="text-xs-center p-5">
          <h4>Drag and drop here to upload<br/>or</h4>
          <label :for="schema.id" class="v-btn primary"><div class="v-btn__content">Select File</div></label>
        </div>

        <div v-show="$refs.upload && $refs.upload.dropActive" class="drop-active">
          <h3>Drop file to upload</h3>
        </div>

        <div class="file-upload-btn">
          <file-upload
              class="btn btn-primary"
              :post-action="postUrl"
              :multiple="false"
              :drop="true"
              :data="formData"
              v-model="value"
              :inputId="schema.id"
              ref="upload">
            <i class="fa fa-plus"></i>
            Select file
          </file-upload>
        </div>
        <div v-if="schema.hint" class="input-group__messages input-group__hint">{{hint}}</div>
        <div v-if="errors.length" class="input-group__messages input-group__error">{{errors.join(', ')}}</div>
      </div>
    </v-card-text>
  </v-card>
</template>
<style scoped>
  .example-drag label.btn {
    margin-bottom: 0;
    margin-right: 1rem;
  }

  .example-drag .drop-active {
    top: 0;
    bottom: 0;
    right: 0;
    left: 0;
    position: fixed;
    z-index: 9999;
    opacity: .6;
    text-align: center;
    background: #000;
  }

  .example-drag .drop-active h3 {
    margin: -.5em 0 0;
    position: absolute;
    top: 50%;
    left: 0;
    right: 0;
    -webkit-transform: translateY(-50%);
    -ms-transform: translateY(-50%);
    transform: translateY(-50%);
    font-size: 40px;
    color: #fff;
    padding: 0;
  }
  .file-upload-btn {
    display: none;
  }
</style>

<script>
  import { abstractField } from 'vue-form-generator'
  import materialField from './materialField'
  import FileUpload from 'vue-upload-component'
  import {EventBus} from '../../lib'

  export default {
    mixins: [abstractField, materialField],
    components: {
      FileUpload
    },
    data () {
      return {
        formData: {},
        postUrl: ''
      }
    },
    watch: {
      value () {
        this.errors = []
      }
    },
    methods: {
      getUrl (file) {
        return URL.createObjectURL(file.file)
      }
    },
    created () {
      EventBus.$on('submit-' + this.schema.uniqueId, this.upload)
      window.uploader = this
    },
    destroyed () {
      EventBus.$off('submit-' + this.schema.uniqueId, this.upload)
    }
  }
</script>
