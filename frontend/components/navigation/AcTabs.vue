<template>
  <v-container fluid class="pa-0">
    <v-tabs grow centered show-arrows class="hidden-sm-and-down" v-model="tab">
      <ac-tab v-for="item in items" :key="item.text" :count="item.count" :icon="item.icon" :value="item">
        {{item.text}}
      </ac-tab>
    </v-tabs>
    <v-select :items="items"
              v-model="tab"
              :prepend-inner-icon="(tab && tab.icon) || ''"
              class="hidden-md-and-up"
              :item-text="renderText"
    />
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import {TabNavSpec} from '@/types/TabNavSpec'
import {RawLocation, Route} from 'vue-router'
import AcTab from '@/components/AcTab.vue'
import {TabSpec} from '@/types/TabSpec'
@Component({
  components: {AcTab},
})
export default class AcTabs extends Vue {
  @Prop({required: true})
  public value!: number
  @Prop({required: true})
  public items!: TabSpec[]

  public renderText(item: TabSpec) {
    if (item.count) {
      return `${item.text} (${item.count})`
    }
    return item.text
  }

  public get tab() {
    // Match the name or any parent route name. Ignores params.
    return this.value
  }
  public set tab(val: number) {
    this.$emit('input', val)
  }
}
</script>
