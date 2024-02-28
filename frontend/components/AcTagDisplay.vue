<template xmlns:v-slot="http://www.w3.org/1999/XSL/Transform">
  <v-container fluid class="pa-0">
    <v-row dense>
      <v-col>
        <v-tooltip top v-if="controls">
          <template v-slot:activator="{props}" aria-label="Tooltip for tags">
            <v-btn color="primary" icon size="small" v-bind="props" @click="editTags" class="edit-button" aria-label="Edit tags">
              <v-icon size="x-large" icon="mdi-tag-multiple"/>
            </v-btn>
          </template>
          Edit Tags
        </v-tooltip>
        <v-tooltip top v-else aria-label="Tooltip for tags">
          <template v-slot:activator="{props}">
            <v-icon v-bind="props" icon="mdi-tag-multiple" aria-label="Tags"/>
          </template>
          Tags
        </v-tooltip>
        <v-chip v-for="tag in displayedTags" :key="tag" @click.stop="setSearch(tag)" class="tag-search-link ml-2">
          <ac-link :to="tagLink(tag)">{{tag}}</ac-link>
        </v-chip>
        <v-chip v-if="moreTags" @click="showMore" class="show-more-tags ml-2">...</v-chip>
      </v-col>
      <v-col v-if="displayedTags.length === 0">
        <span>
          &nbsp;
          <span v-if="controls">No tags set. Please add some!</span>
          <span v-else>No tags set.</span>
        </span>
      </v-col>
      <ac-expanded-property v-model="toggle" aria-label="Tag Editing Dialog">
        <template v-slot:title>
          All Tags
        </template>
        <v-row>
          <v-col cols="12" v-if="editing && controls">
            <ac-patch-field field-type="ac-tag-field" :patcher="patcher"/>
          </v-col>
          <v-col cols="12" v-show="!editing">
            <v-chip v-for="tag in patcher.rawValue" :key="tag" class="mx-1" :color="$vuetify.theme.current.colors['well-darken-4']">
              <ac-link :to="tagLink(tag)">{{tag}}</ac-link>
            </v-chip>
          </v-col>
        </v-row>
        <template v-slot:actions>
          <v-switch v-model="editing" label="Editing" v-if="controls" color="primary"/>
          <v-spacer/>
          <v-btn color="primary" type="submit" variant="flat">
            Done
          </v-btn>
        </template>
      </ac-expanded-property>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import AcTagField from '@/components/fields/AcTagField.vue'
import {Patch} from '@/store/singles/patcher.ts'
import Subjective from '@/mixins/subjective.ts'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import {FormController} from '@/store/forms/form-controller.ts'

@Component({
  components: {
    AcLink,
    AcPatchField,
    AcExpandedProperty,
    AcTagField,
  },
})
class AcTagDisplay extends mixins(Subjective) {
  public searchForm: FormController = null as unknown as FormController
  @Prop({required: true})
  public patcher!: Patch

  @Prop({default: false})
  public editable!: boolean

  @Prop({required: true})
  public scope!: string

  public toggle = false
  public editing = false

  public editTags() {
    this.toggle = true
    this.editing = true
  }

  public showMore() {
    this.editing = false
    this.toggle = true
  }

  public setSearch(tag: string) {
    this.searchForm.reset()
    this.searchForm.fields.q.update(tag)
    this.$router.push(this.tagLink(tag))
  }

  public tagLink(tag: string) {
    return {
      name: 'Search' + this.scope,
      query: {q: tag},
    }
  }

  public get displayedTags() {
    return this.patcher.rawValue.slice(0, 10)
  }

  public get controls() {
    if (this.editable && this.isRegistered) {
      return true
    }
    if (this.isCurrent) {
      return true
    }
    return this.isStaff
  }

  public get moreTags() {
    return this.patcher.rawValue.length - this.displayedTags.length
  }

  public created() {
    this.searchForm = this.$getForm('search')
  }
}

export default toNative(AcTagDisplay)
</script>
