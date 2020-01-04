<template>
  <ac-form-container :sending="fieldController.form.sending" :errors="fieldController.form.errors">
    <v-row no-gutters>
      <slot name="preview" :item="item" v-for="item in listController.list">
        <v-col cols="12">{{item}}</v-col>
      </slot>
      <slot name="empty" v-if="listController.empty">
      </slot>
      <v-col cols="12">
        <slot :filter="filter" />
      </v-col>
    </v-row>
  </ac-form-container>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop, Watch} from 'vue-property-decorator'
import {ListController} from '@/store/lists/controller'
import {FieldController} from '@/store/forms/field-controller'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {SingleController} from '@/store/singles/controller'
  @Component({
    components: {AcFormContainer},
  })
export default class AcRelatedManager extends Vue {
    @Prop({required: true})
    public listController!: ListController<any>
    @Prop({required: true})
    public fieldController!: FieldController

    public filter(entry: {id: number}, queryText: string, itemText: string) {
      if (!queryText) {
        return false
      }
      if (this.listController.list.map((item: SingleController<any>) => item.x.id).indexOf(entry.id) !== -1) {
        return false
      }
      return itemText.toLocaleLowerCase().indexOf(queryText.toLocaleLowerCase()) > -1
    }

    @Watch('fieldController.value')
    public autoSubmit(newVal: number|null) {
      if (newVal === null) {
        return
      }
      this.fieldController.form.submitThen(this.listController.uniquePush).then()
    }
}
</script>
