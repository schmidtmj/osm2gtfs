# coding=utf-8

import copy, logging
from osm2gtfs.creators.trips_creator import TripsCreator


class TripsCreatorGhAccra2(TripsCreator):

    def add_trips_to_feed(self, feed, data):
        """
        This function generates and adds trips to the GTFS feed.

        It is the place where geographic information and schedule is
        getting joined to produce a routable GTFS.

        The default format of the schedule information:
        https://github.com/grote/osm2gtfs/wiki/Schedule
        """
        all_trips_count = 0

        # Go though all lines
        for line_id, line in data.routes.iteritems():

            logging.info("\nGenerating schedule for line: [" + line_id + "] - " + line.name)

            # Loop through it's itineraries
            itineraries = line.get_itineraries()
            for itinerary in itineraries:
                trips_count = 0

                # Verify data before proceeding
                if self._verify_data(data.schedule, line, itinerary):

                    # Prepare itinerary's trips and schedule
                    prepared_trips = self._prepare_trips(feed, data.schedule,
                                                         itinerary)

                    # Add itinerary shape to feed.
                    shape_id = self._add_shape_to_feed(
                        feed, itinerary.osm_type + "/" + str(
                            itinerary.osm_id), itinerary)

                    # Add trips of each itinerary to the GTFS feed
                    for trip_builder in prepared_trips:

                        trip_builder['all_stops'] = self._update_stop_names(data, itinerary)
                        trips_count += self._add_itinerary_trips(
                            feed, itinerary, line, trip_builder, shape_id)

                # Print out status messge about added trips
                logging.info(" Itinerary: [" + itinerary.route_id.encode("utf-8") + "] " +
                             itinerary.to.encode("utf-8") + " (added " + str(
                                 trips_count) + " trips, serving " + str(
                                     len(itinerary.get_stops())) + " stops) - " +
                             itinerary.osm_url)
                all_trips_count += trips_count

        logging.info("\nTotal of added trips to this GTFS: %s\n\n", str(all_trips_count))
        return

    def _update_stop_names(self, data, itinerary):
        """
        This function fixes discrepancies between from/to tags in OSM relations and actual stop names.
        It is mainly a hack and it would be better if stop names were rectified within OSM to match the from/to tags within the route relations.
        """
        itiner_stops = itinerary.get_stops()
        all_stops = copy.deepcopy(data.get_stops())
        assert len(all_stops['stations']) == 0 # There shouldn't be any stations but make sure that doesn't change in the future

        fr= itinerary.fr.decode('utf-8')
        to = itinerary.to.decode('utf-8')
        stop_first = all_stops['regular'][itiner_stops[0]]
        stop_last = all_stops['regular'][itiner_stops[-1]]

        if stop_first.name.decode('utf-8') != fr:
            logging.info("Changed first stop name from {} to {}".format(stop_first.name, fr))
            stop_first.name = fr
        if stop_last.name.decode('utf-8') != to:
            logging.info("Changed last stop name from {} to {}".format(stop_last.name, to))
            stop_last.name = to
        return all_stops
