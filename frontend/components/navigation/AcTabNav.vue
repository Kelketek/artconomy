<template>
  <v-container fluid class="pa-0">
    <v-tabs grow centered show-arrows class="hidden-sm-and-down">
      <ac-tab :to="item.value" v-for="item in items" :key="item.text" :count="item.count" :icon="item.icon">
        {{item.text}}
      </ac-tab>
    </v-tabs>
    <v-select :items="items"
              v-model="tab"
              :prepend-inner-icon="tab && tab.icon"
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
  @Component({
    components: {AcTab},
  })
export default class AcTabNav extends Vue {
    @Prop({required: true})
    public items!: TabNavSpec[]

    public renderText(item: TabNavSpec) {
      if (item.count) {
        return `${item.text} (${item.count})`
      }
      return item.text
    }

    public get tab() {
      // Match the name or any parent route name. Ignores params.
      return this.items.filter(
        (item) => this.$route.matched.filter((match) => match.name === item.value.name).length)[0]
    }

    public set tab(val) {
      this.$router.replace(val as RawLocation)
    }
}
</script>
