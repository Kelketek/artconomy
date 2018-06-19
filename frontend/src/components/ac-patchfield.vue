<template>
    <v-flex class="patchfield-wrapper" :class="classes()">
      <v-flex v-if="editmode && multiline" @click="startEditing">
        <v-text-field ref="field" :multi-line="true" @keydown="handleMultilineInput" append-icon="edit" :append-icon-cb="focusField" v-model="input" @input="resizer" :v-focus="true" @blur="save" @keyup.escape="reset" :disabled="disabled"></v-text-field>
      </v-flex>
      <v-flex v-else-if="editmode" @click="startEditing">
        <v-text-field type="text" ref="field" class="patch-input" append-icon="edit" :append-icon-cb="focusField" v-model="input" @keyup.enter.native="save" :autofocus="true" @focus="setAtEnd" :value="value" @blur="save" @keyup.escape.native="reset" :disabled="disabled" />
      </v-flex>
      <v-flex v-else-if="multiline" class="patchfield-normal" v-html="preview"></v-flex>
      <v-flex v-else class="patchfield-normal" v-html="preview"></v-flex>
    </v-flex>
</template>

<script>
  import { focus } from 'vue-focus'
  import {artCall} from '../lib'
  import autosize from 'autosize'
  import Vue from 'vue'

  export default {
    name: 'ac-patchfield',
    directives: { focus: focus },
    props: ['value', 'editmode', 'name', 'styleclass', 'url', 'callback', 'multiline', 'placeholder', 'displayValue'],
    data: function () {
      return {
        editing: false,
        original: this.value,
        disabled: false,
        errors: [],
        input: this.value
      }
    },
    computed: {
      preview: function () {
        let value = this.value
        if (this.displayValue !== undefined) {
          value = this.displayValue
        }
        if (!value && this.editmode) {
          value = this.placeholder ? this.placeholder : ''
        }
        if (this.multiline) {
          return this.$root.md.render(value + '')
        } else {
          return this.$root.md.renderInline(value + '')
        }
      }
    },
    methods: {
      focusField () {
        this.$refs.field.focus()
      },
      update () {
        this.$emit('input', this.input)
      },
      resizer () {
        autosize(this.$refs.field)
      },
      setAtEnd () {
        // By resetting the value to a blank string and then re-setting it, we force the cursor at the end of the field.
        let value = this.$refs.field.value
        this.$refs.field.$refs.input.value = ''
        this.$refs.field.$refs.input.value = value
      },
      formatErrors () {
        let errors = ''
        for (let [index, error] of Array.entries(this.errors)) {
          errors += error
          if (index + 1 < errors.length) {
            errors += '\n'
          }
        }
        return errors
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
        this.errors = []
        if (this.original === this.input) {
          this.editing = false
          return
        }
        this.update()
        let data = {}
        this.disabled = true
        data[this.name] = this.input
        artCall(this.url, 'PATCH', data, this.postSave, this.postFail)
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
      postFail (response) {
        this.editing = false
        this.disabled = false
        if (response.responseJSON && response.responseJSON !== undefined) {
          this.errors = response.responseJSON[this.name] || ['There was an issue while saving. Please try again later.']
        } else {
          this.errors = ['There was an issue while saving. Please try again later.']
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
    },
    watch: {
      value (value) {
        this.input = value
      }
    }
  }
</script>

<style>
  .patchfield-preview {
    display: inline-block;
  }
  textarea.patchfield-multiline-editor {
    width: 100%;
    height: 100%;
  }
  .patchfield-wrapper {
    display: inline-block;
  }
  .patchfield-wrapper .input-group__details {
    display: none
  }
  .patch-input {
    padding-top: 0;
    padding-bottom: 0;
    padding-left: 0;
    padding-right: 0;
    max-height: 1em;
  }
  .patch-input input {
    font-size: inherit;
  }
  .error-marker {
    color: red;
  }
  .patchfield-multiline-wrapper {
    width: 100%;
    height: available;
  }
</style>
