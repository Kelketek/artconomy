<template>
  <v-layout row wrap class="attr-set">
    <template v-for="attribute in stickyAttributes">
      <v-flex xs3 :key="attribute.id" class="attr-key attr-sticky">{{attribute.key}}</v-flex>
      <v-flex xs8>
        <ac-patchfield v-model="attribute.value" name="value" :editmode="editMode" :url="`${url}${attribute.id}/`" :callback="success" class="attr-value"></ac-patchfield>
      </v-flex>
      <v-flex xs12><v-divider></v-divider></v-flex>
    </template>
    <template v-for="attribute in unstickyAttributes">
      <v-flex xs3 :key="attribute.id" class="attr-key"><ac-patchfield v-model="attribute.key" name="key" :editmode="editMode" :url="`${url}${attribute.id}/`" :callback="success" /></v-flex>
      <v-flex xs8>
        <ac-patchfield v-model="attribute.value" name="value" :editmode="editMode" :url="`${url}${attribute.id}/`" :callback="success" class="attr-value" />
      </v-flex>
      <v-flex xs1 v-if="editMode">
        <ac-action :url="`${url}${attribute.id}/`" :button="false" :success="success" method="DELETE">
          <v-icon>delete</v-icon>
        </ac-action>
      </v-flex>
      <v-flex xs12><v-divider></v-divider></v-flex>
    </template>
    <v-flex xs3 class="attr-key new-attr" v-if="editMode && canAdd" @keydown.enter="save">
      <v-text-field
          ref="keyField"
          placeholder="Attribute"
          v-model="newKey"
          :class="{'input-group--error': errors.key.length, 'error--text': errors.key.length}"
          append-icon="edit"
          @click:append="focusKey"
      >
      </v-text-field>
    </v-flex>
    <v-flex xs8 class="new-attr" v-if="editMode && canAdd" @keydown.enter="save">
      <v-text-field
          ref="valueField"
          v-model="newValue"
          placeholder="Value"
          append-icon="edit"
          @click:append="focusValue"
          :class="{'input-group--error': errors.value.length, 'error--text': errors.value.length}"
      ></v-text-field>
    </v-flex>
    <v-flex xs1 class="new-attr" v-if="editMode && canAdd">
      <v-icon :class="{'attr-save-disabled': !canSubmit}" @click="save">save</v-icon>
    </v-flex>
    <v-flex xs12 v-if="editMode && canAdd">
      <v-divider></v-divider>
    </v-flex>
  </v-layout>
</template>

<script>
  import AcPatchfield from './ac-patchfield'
  import AcAction from './ac-action'
  import {artCall} from '../lib'

  export default {
    name: 'ac-attributes',
    components: {AcAction, AcPatchfield},
    props: ['attributes', 'url', 'editMode', 'success'],
    data () {
      return {
        newKey: '',
        newValue: '',
        errors: {key: [], value: []}
      }
    },
    methods: {
      save () {
        if (!this.canSubmit) {
          return
        }
        artCall(this.url, 'POST', {key: this.newKey, value: this.newValue}, this.postSave, this.fail)
      },
      focusKey () {
        this.$refs.keyField.focus()
      },
      focusValue () {
        this.$refs.valueField.focus()
      },
      postSave () {
        this.$refs.keyField.$refs.input.focus()
        this.newKey = ''
        this.newValue = ''
        this.errors = {key: [], value: []}
        this.success()
      },
      fail (response) {
        if (response.responseJSON) {
          if (response.responseJSON.key) {
            this.errors.key = response.responseJSON.key
          }
          if (response.responseJSON.value) {
            this.errors.value = response.responseJSON.value
          }
          if (response.responseJSON.detail) {
            this.errors.value.push(response.responseJSON.detail)
            this.errors.key.push(response.responseJSON.detail)
          }
        } else {
          this.errors.key = ['Failed.']
          this.errors.value = ['Failed.']
        }
      }
    },
    computed: {
      stickyAttributes () {
        return this.attributes.filter((x) => { return x.sticky })
      },
      unstickyAttributes () {
        return this.attributes.filter((x) => { return !x.sticky })
      },
      canAdd () {
        return this.attributes.length < 10
      },
      canSubmit () {
        return this.newKey && this.newValue
      }
    }
  }
</script>

<style>
  .attr-key {
    text-transform: uppercase;
    font-weight: bold;
  }
  .new-attr .v-input, .new-attr.input-group {
    padding: 0;
  }
  .attr-set .v-text-field .v-input__slot::after, .attr-set .v-text-field .v-input__slot::before {
    display: none;
  }
  .new-attr .v-input {
    font-size: inherit;
    margin: 0;
  }
  .new-attr .v-input__slot {
    padding: 0;
    margin: 0;
  }
  .new-attr .v-text-field__slot input {
    font-size: inherit;
    padding: 0;
  }
  .attr-key .v-input input {
    text-transform: uppercase;
    margin-top: 0;
    margin-bottom: 0;
  }
  .patchfield-wrapper.attr-value {
    width: 100%;
  }
  .new-attr .v-text-field__details {
    display: none;
  }
  .attr-set .error--text input {
    color: red
  }
  .attr-save-disabled {
    opacity: .5;
  }
</style>