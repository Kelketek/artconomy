<template>
    <div class="patchfield-wrapper" :class="classes()">
      <div v-if="editing && multiline"><textarea style="width: 100%;" class="patchfield-multiline-editor" @keydown="handleMultilineInput" ref="field" @input="resizer" v-focus="true" :value="value" @blur="save" @keyup.escape="reset" :disabled="disabled"></textarea></div>
      <div v-else-if="editing"><input type="text" class="patch-input" ref="field" @keyup.enter="save" v-focus="true" :value="value" @blur="save" @keyup.escape="reset" :disabled="disabled"></div>
      <div v-else-if="editmode" @click="startEditing"><div class="patchfield-preview" :class="{'patchfield-preview-multiline': multiline}" tabindex="0" @focus="startEditing" @input="update" v-html="preview"></div><i class="fa fa-pencil" style="padding-left: 1em;"></i></div>
      <div v-else-if="multiline" class="patchfield-normal" v-html="preview"></div>
      <div v-else class="patchfield-normal" v-html="preview"></div>
    </div>
</template>

<script>
  import { focus } from 'vue-focus'
  import {artCall} from '../lib'
  import autosize from 'autosize'
  import Vue from 'vue'

  export default {
    name: 'ac-patchfield',
    directives: { focus: focus },
    props: ['value', 'editmode', 'name', 'styleclass', 'url', 'callback', 'multiline'],
    data: function () {
      return {
        editing: false,
        original: this.value,
        disabled: false
      }
    },
    computed: {
      preview: function () {
        let initial = this.$root.md.render(this.value)
        if (this.multiline) {
          return initial
        } else {
          let container = document.createElement('div')
          container.innerHTML = initial
          return container.firstChild.innerHTML
        }
      }
    },
    methods: {
      update () {
        this.$emit('input', this.$refs.field.value)
      },
      resizer () {
        autosize(this.$refs.field)
      },
      startEditing () {
        this.editing = true
        let self = this
        Vue.nextTick(() => {
          self.resizer()
        })
      },
      reset () {
        this.$refs.field.value = this.original
        this.update()
        this.editing = false
      },
      save () {
        if (this.original === this.$refs.field.value) {
          this.editing = false
          return
        }
        this.update()
        let data = {}
        this.disabled = true
        data[this.name] = this.$refs.field.value
        artCall(this.url, 'PATCH', data, this.postSave)
      },
      handleMultilineInput (event) {
        if (event.keyCode === 13) {
          if (!this.multiline) {
            event.preventDefault()
            this.save()
          } else if (event.shiftKey) {
          } else {
            event.preventDefault()
            this.save()
          }
        }
      },
      postSave () {
        this.editing = false
        this.original = this.value
        this.disabled = false
        if (this.callback) {
          this.callback()
        }
      },
      classes () {
        let styles = {}
        if (this.multiline) {
          styles['patchfield-multiline-wrapper'] = true
        }
        if (this.styleclass) {
          styles[this.styleclass] = true
        }
        return styles
      }
    }
  }
</script>

<style lang="scss">
  @import '../custom-bootstrap';
  .patchfield-preview {
    display: inline-block;
  }
  input.patch-input {
    padding: 0;
    margin: 0;
    background-color: $light-gray;
    border-color: $dark-purple;
    border-top: none;
    border-right: none;
    border-left: none;
    height: 1em;
    box-sizing: border-box;
  }
  textarea.patchfield-multiline-editor {
    width: 100%;
    height: 100%;
  }
  .patchfield-wrapper {
    display: inline-block;
  }
  .patchfield-multiline-wrapper {
    width: 100%;
    height: available;
  }
</style>
