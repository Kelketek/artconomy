<template>
  <v-container fluid class="pa-0">
    <v-tabs grow centered show-arrows class="hidden-sm-and-down" v-model="tab">
      <ac-tab v-for="item in items" :key="item.title" :count="item.count" :icon="item.icon" :value="item.value">
        {{item.title}}
      </ac-tab>
    </v-tabs>
    <v-select :items="items"
              v-model="tab"
              :label="label"
              :prepend-inner-icon="(tabSpec && tabSpec.icon) || ''"
              class="hidden-md-and-up"
              :item-text="renderText"
    />
  </v-container>
</template>

<script lang="ts">
import {Component, Prop, toNative, Vue} from 'vue-facing-decorator'
import AcTab from '@/components/AcTab.vue'
import {TabSpec} from '@/types/TabSpec'

@Component({
  components: {AcTab},
  emits: ['update:modelValue'],
})
class AcTabs extends Vue {
  @Prop({required: true})
  public label!: string

  @Prop({required: true})
  public modelValue!: number

  @Prop({required: true})
  public items!: TabSpec[]

  public renderText(item: TabSpec) {
    if (item.count) {
      return `${item.title} (${item.count})`
    }
    return item.title
  }

  public get tabSpec() {
    return this.items[this.tab]
  }

  public get tab() {
    // Match the name or any parent route name. Ignores params.
    return this.modelValue
  }

  public set tab(val: number) {
    this.$emit('update:modelValue', val)
  }
}

export default toNative(AcTabs)
</script>
